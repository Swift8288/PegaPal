"""
RAG Query Engine — Retrieves relevant chunks from ChromaDB,
then generates a debugging answer via Groq (free) or Claude (BYOK).
Supports conversation history for contextual follow-up questions.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    LLM_BACKEND,
    SYSTEM_PROMPT,
    TOP_K,
)
from indexer.index_docs import PegaIndexer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class DebugResult:
    """Structured result from the RAG pipeline."""
    answer: str
    confidence: str  # "HIGH", "MEDIUM", "LOW"
    sources: list[dict] = field(default_factory=list)
    context_chunks: list[str] = field(default_factory=list)
    llm_backend: str = ""


# ── LLM Backends (with conversation history support) ──────────────────

def _call_groq(messages: list[dict], system: str = SYSTEM_PROMPT) -> str:
    """Call Groq API with full message history."""
    import httpx
    from groq import Groq

    http_client = httpx.Client(timeout=60.0)
    client = Groq(api_key=GROQ_API_KEY, http_client=http_client)
    try:
        full_messages = [{"role": "system", "content": system}] + messages
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=full_messages,
            temperature=0.2,
            max_tokens=2048,
        )
        return response.choices[0].message.content
    finally:
        http_client.close()


def _call_groq_raw(messages: list[dict], system: str = SYSTEM_PROMPT) -> str:
    """Fallback: call Groq API directly via HTTP if SDK fails."""
    import requests

    full_messages = [{"role": "system", "content": system}] + messages
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": GROQ_MODEL,
            "messages": full_messages,
            "temperature": 0.2,
            "max_tokens": 2048,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _call_claude(messages: list[dict], system: str = SYSTEM_PROMPT) -> str:
    """Call Claude API with full message history."""
    import httpx
    import anthropic

    http_client = httpx.Client(timeout=60.0)
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, http_client=http_client)
    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2048,
            system=system,
            messages=messages,
            temperature=0.2,
        )
        return response.content[0].text
    finally:
        http_client.close()


def _call_openai(messages: list[dict], system: str = SYSTEM_PROMPT) -> str:
    """Call OpenAI-compatible API (GPT-4o)."""
    import requests
    import importlib
    cfg = importlib.import_module("config")
    api_key = cfg.OPENAI_API_KEY

    full_messages = [{"role": "system", "content": system}] + messages
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o",
            "messages": full_messages,
            "temperature": 0.2,
            "max_tokens": 2048,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _call_gemini(messages: list[dict], system: str = SYSTEM_PROMPT) -> str:
    """Call Google Gemini API."""
    import requests
    import importlib
    cfg = importlib.import_module("config")
    api_key = cfg.GEMINI_API_KEY

    # Convert chat messages to Gemini format
    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    resp = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
        headers={"Content-Type": "application/json"},
        json={
            "system_instruction": {"parts": [{"text": system}]},
            "contents": contents,
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048},
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"]


def _is_rate_limit_error(error: Exception) -> bool:
    """Check if an error is a rate limit (429) error."""
    error_str = str(error).lower()
    return (
        "429" in error_str
        or "rate_limit" in error_str
        or "rate limit" in error_str
        or "quota" in error_str
        or "resource_exhausted" in error_str
    )


def _get_available_backends() -> list[tuple[str, str]]:
    """
    Return list of (backend_name, display_name) for backends that have
    API keys configured. Ordered by preference: groq, gemini, openai, claude.
    Reads live config values (picks up keys entered via sidebar at runtime).
    """
    import importlib
    cfg = importlib.import_module("config")
    # Note: do NOT reload — sidebar sets keys via setattr, reload would wipe them

    available = []
    if getattr(cfg, "GROQ_API_KEY", ""):
        available.append(("groq", "Groq (Llama 3.3 70B)"))
    if getattr(cfg, "GEMINI_API_KEY", ""):
        available.append(("gemini", "Google Gemini 1.5 Pro"))
    if getattr(cfg, "OPENAI_API_KEY", ""):
        available.append(("openai", "OpenAI GPT-4o"))
    if getattr(cfg, "ANTHROPIC_API_KEY", ""):
        available.append(("claude", "Claude Sonnet"))
    return available


# Map of backend name → call function
_BACKEND_CALLERS = {
    "groq": _call_groq,
    "claude": _call_claude,
    "openai": _call_openai,
    "gemini": _call_gemini,
}


def call_llm(messages: list[dict], backend: Optional[str] = None) -> tuple[str, str]:
    """
    Route to the configured LLM backend with full conversation history.
    Returns (response_text, backend_name).

    Auto-fallback: if the primary backend fails with a rate limit error,
    automatically tries other backends that have API keys configured.
    Supports: groq, claude, openai, gemini
    """
    import importlib
    cfg = importlib.import_module("config")
    primary = backend or LLM_BACKEND

    # Build the fallback order: primary first, then all other available backends
    available = _get_available_backends()
    if not available:
        raise ValueError(
            "No API keys configured. Enter at least one API key in the sidebar.\n\n"
            "Free options:\n"
            "• **Groq** — [console.groq.com](https://console.groq.com) (Llama 3.3 70B, free)\n"
            "• **Google Gemini** — [aistudio.google.com](https://aistudio.google.com/apikey) (Gemini 1.5 Pro, free)"
        )

    # Put the user's preferred backend first in the fallback chain
    available_names = [b[0] for b in available]
    if primary in available_names:
        # Move primary to front
        order = [primary] + [b for b in available_names if b != primary]
    else:
        # Primary has no key — warn and use what's available
        logger.warning(f"Selected backend '{primary}' has no API key, using available backends")
        order = available_names

    # Try each backend in order
    last_error = None
    for i, backend_name in enumerate(order):
        caller = _BACKEND_CALLERS.get(backend_name)
        if not caller:
            continue

        try:
            if backend_name == "groq":
                # Groq has SDK + raw HTTP fallback
                try:
                    result = _call_groq(messages)
                except TypeError as e:
                    logger.warning(f"Groq SDK failed ({e}), trying raw HTTP")
                    result = _call_groq_raw(messages)
            else:
                result = caller(messages)

            if i > 0:
                logger.info(f"Fallback succeeded: {backend_name} (after {order[:i]} failed)")
            return result, backend_name

        except Exception as e:
            last_error = e
            if _is_rate_limit_error(e):
                logger.warning(f"Rate limit on {backend_name}: {e}")
                if i < len(order) - 1:
                    next_backend = order[i + 1]
                    logger.info(f"Auto-fallback: {backend_name} → {next_backend}")
                    continue  # Try the next backend
            else:
                # Non-rate-limit errors: still try fallback but log as error
                logger.error(f"LLM error on {backend_name}: {e}")
                if i < len(order) - 1:
                    continue

    # All backends failed
    raise last_error or ValueError("All LLM backends failed.")


# ── Query Preprocessing ────────────────────────────────────────────────

def extract_search_query(question: str, chat_history: list[dict] = None) -> str:
    """
    Extract the core search query from structured or verbose input.
    If it's a short follow-up, combine with the previous question for context.
    """
    lines = question.strip().split("\n")
    error_msg = ""
    where = ""

    for line in lines:
        line_lower = line.lower().strip()
        if line_lower.startswith("error message:") or line_lower.startswith("error:"):
            error_msg = line.split(":", 1)[1].strip()
        elif line_lower.startswith("where it happens:") or line_lower.startswith("where:"):
            where = line.split(":", 1)[1].strip()

    # If we found structured fields, build a focused search query
    if error_msg:
        search_query = error_msg
        if where:
            search_query += f" in {where}"
        return search_query

    # For short follow-up questions, add context from previous exchange
    if chat_history and len(question.split()) < 10:
        # Look for the last user question to add context
        for msg in reversed(chat_history):
            if msg["role"] == "user":
                prev_query = extract_search_query(msg["content"])
                # Combine: "what about version 24?" + prev context "SMA admin console"
                return f"{question} {prev_query}"

    return question


# ── Confidence Estimation ──────────────────────────────────────────────

def estimate_confidence(hits: list[dict]) -> str:
    """
    Estimate answer confidence based on retrieval quality.
    Uses cosine distance from ChromaDB (lower = better match).
    Calibrated for real-world queries which are often short, abbreviated,
    or use different wording than KB titles. A 35%+ match with relevant
    sources produces good answers.
    """
    if not hits:
        return "LOW"

    best_distance = hits[0]["distance"]

    # Thresholds calibrated for TF-IDF and SBERT with real user queries:
    # - Users type abbreviated errors ("index of outbound" vs "IndexOutOfBoundsException")
    # - Short queries (3-5 words) naturally score lower similarity
    # - 35%+ match (distance < 0.65) reliably pulls relevant context
    if best_distance < 0.65:
        return "HIGH"
    elif best_distance < 0.82:
        return "MEDIUM"
    else:
        return "LOW"


# ── RAG Pipeline ───────────────────────────────────────────────────────

def build_context_prompt(query: str, hits: list[dict]) -> str:
    """Build the augmented prompt with retrieved context and match quality."""
    context_blocks = []
    match_scores = []
    for i, hit in enumerate(hits, 1):
        source = hit["metadata"].get("title", hit["metadata"].get("url", "Unknown"))
        match_pct = (1 - hit["distance"]) * 100
        match_scores.append(match_pct)
        context_blocks.append(
            f"--- Source {i}: {source} (match: {match_pct:.0f}%) ---\n{hit['document']}"
        )

    context = "\n\n".join(context_blocks)
    best_match = max(match_scores) if match_scores else 0
    avg_match = sum(match_scores) / len(match_scores) if match_scores else 0

    # Add match quality guidance
    if best_match < 30:
        quality_note = f"""
IMPORTANT: The best KB match is only {best_match:.0f}%. This means the knowledge base likely does NOT have relevant content for this question. If the question is vague or ambiguous, ask the user to be more specific. If you can still answer from general Pega knowledge, do so but note it's not from the KB."""
    elif best_match < 50:
        quality_note = f"""
NOTE: Best KB match is {best_match:.0f}% (moderate). The context may be partially relevant. Use what's relevant, supplement with your Pega expertise, and be transparent about confidence."""
    else:
        quality_note = f"""
KB match quality: {best_match:.0f}% (good). Use the context to provide a grounded answer."""

    return f"""Use the context below to answer the user's question. The context may not mention the exact term — use RELATED information to provide a helpful answer. Only say you can't help if the context is completely irrelevant.
{quality_note}

=== CONTEXT FROM KNOWLEDGE BASE ===
{context}
=== END CONTEXT ===

User's Question:
{query}

Answer directly and specifically. Match your response style to the question type:
- If the question is vague (e.g., "give me a plan", "sample template") with no specific Pega topic, ask the user to clarify what topic they want — suggest 3-5 specific options.
- If it's an error or debugging question: explain the error, common causes, and step-by-step debugging instructions.
- If it's a concept or "explain" question: give a clear explanation with examples and best practices.
- If it's a how-to question: provide step-by-step instructions.
- If it's a comparison: give a balanced comparison with recommendations.
Cite source numbers when referencing information."""


def build_general_prompt(query: str) -> str:
    """Build a prompt for general Pega questions when KB has no good match."""
    return f"""The knowledge base didn't have a strong match for this question.

User's Question:
{query}

Instructions:
- If the question is vague or ambiguous (e.g., "give me a plan", "sample template", "explain this" without a specific topic), ask the user to clarify. Suggest 3-5 specific Pega topics they might be asking about.
- If the question is specific enough, answer it directly using your Pega platform expertise.
- Be specific and practical — give actionable information.
- If this is a comparison or conceptual question, give a balanced answer.
- If you're not confident about something, say so.
- Do NOT cite sources (since this answer is from general knowledge, not the KB)."""


class PegaDebugEngine:
    """Main RAG engine — ties retrieval + generation together."""

    def __init__(self, embedding_backend: Optional[str] = None):
        self.indexer = PegaIndexer(backend=embedding_backend)
        logger.info(f"Debug engine ready — {self.indexer.stats()['total_chunks']} chunks in KB")

    def query(
        self,
        question: str,
        top_k: int = TOP_K,
        llm_backend: Optional[str] = None,
        chat_history: list[dict] = None,
    ) -> DebugResult:
        """
        Full RAG pipeline with conversation history:
        1. Extract search query (with follow-up context)
        2. Embed query → search ChromaDB
        3. Build augmented prompt with conversation history
        4. Call LLM with full message history
        5. Return structured result
        """
        chat_history = chat_history or []

        # Step 1: Extract core query with conversation context
        search_query = extract_search_query(question, chat_history)
        logger.info(f"Search query: '{search_query}' (from: '{question[:80]}...')")
        hits = self.indexer.search(search_query, top_k=top_k)
        confidence = estimate_confidence(hits)

        # Step 2: Always pass KB context to the LLM — even low matches
        # can contain useful fragments. Let Claude decide what's relevant.
        best_match_pct = (1 - hits[0]["distance"]) * 100 if hits else 0
        use_general_knowledge = not hits  # Only if zero hits
        logger.info(f"Best match: {best_match_pct:.0f}% — passing all {len(hits)} chunks to LLM")

        if use_general_knowledge:
            logger.info("No KB hits at all — pure general knowledge mode")
            current_prompt = build_general_prompt(question)
        else:
            current_prompt = build_context_prompt(question, hits)

        # Step 3: Build message history for the LLM
        messages = []
        recent_history = chat_history[-6:]
        for msg in recent_history:
            if msg["role"] in ("user", "assistant"):
                content = msg["content"]
                if msg["role"] == "assistant" and len(content) > 500:
                    content = content[:500] + "... [truncated]"
                messages.append({"role": msg["role"], "content": content})

        messages.append({"role": "user", "content": current_prompt})

        # Step 4: Generate with full conversation context
        try:
            answer, backend_used = call_llm(messages, backend=llm_backend)
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return DebugResult(
                answer=f"LLM call failed: {e}\n\nRelevant context was found — "
                       f"see sources below for manual debugging.",
                confidence=confidence,
                sources=[h["metadata"] for h in hits],
                context_chunks=[h["document"] for h in hits],
                llm_backend="error",
            )

        # Add disclaimer only when KB had zero hits
        if use_general_knowledge:
            answer = answer + "\n\n---\n*This answer is based on general Pega knowledge, not the curated knowledge base. Verify details in official Pega documentation.*"
            confidence = "GENERAL"
        elif best_match_pct < 35:
            # Low match — answer uses both KB fragments and general knowledge
            confidence = "MEDIUM"

        # Step 5: Package result
        sources = []
        seen_urls = set()
        for h in hits:
            url = h["metadata"].get("url", "")
            if url not in seen_urls:
                seen_urls.add(url)
                sources.append({
                    "title": h["metadata"].get("title", "Unknown"),
                    "url": url,
                    "distance": round(h["distance"], 4),
                })

        return DebugResult(
            answer=answer,
            confidence=confidence,
            sources=sources,
            context_chunks=[h["document"] for h in hits],
            llm_backend=backend_used,
        )


if __name__ == "__main__":
    engine = PegaDebugEngine()
    result = engine.query(
        "You cannot save a page that your session does not hold a lock on"
    )
    print(f"\nConfidence: {result.confidence}")
    print(f"Backend: {result.llm_backend}")
    print(f"\n{result.answer}")
    print(f"\nSources:")
    for s in result.sources:
        print(f"  - {s['title']} ({s['url']})")
