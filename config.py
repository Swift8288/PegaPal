"""
PegaPal — Central Configuration
"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
_CHROMA_SRC = DATA_DIR / "chroma_db"

# On Streamlit Cloud, the app dir may be read-only or have SQLite locking
# issues.  Detect cloud by checking for /mount/src OR a non-writable data dir,
# then copy ChromaDB to /tmp/ so SQLite can acquire write locks.
def _resolve_chroma_dir():
    """Return a writable ChromaDB path, copying to /tmp if necessary."""
    # Quick check: can we write to the source directory?
    try:
        test_file = _CHROMA_SRC / ".write_test"
        _CHROMA_SRC.mkdir(parents=True, exist_ok=True)
        test_file.touch()
        test_file.unlink()
        return _CHROMA_SRC  # Local / writable — use as-is
    except (OSError, PermissionError):
        pass
    # Fallback: copy to /tmp
    tmp = Path("/tmp/chroma_db")
    if not tmp.exists() and _CHROMA_SRC.exists():
        shutil.copytree(_CHROMA_SRC, tmp)
    elif not tmp.exists():
        tmp.mkdir(parents=True, exist_ok=True)
    return tmp

CHROMA_DIR = _resolve_chroma_dir()
RAW_DOCS_DIR = DATA_DIR / "raw_docs"
COMMUNITY_DOCS_DIR = DATA_DIR / "community_docs"
COMMUNITY_META_FILE = DATA_DIR / "community_meta.json"
IDF_FILE = DATA_DIR / "tfidf_idf.json"          # pre-computed IDF weights for TF-IDF embedder

# ── API Keys ───────────────────────────────────────────────────────────
# Support both .env (local) and Streamlit secrets (cloud deployment)
def _get_secret(key: str, default: str = "") -> str:
    """Read from env vars first, then Streamlit secrets (cloud only), then default."""
    val = os.getenv(key, "")
    if val:
        return val
    # Only try st.secrets when deployed to Streamlit Cloud (avoids warnings locally)
    if os.getenv("STREAMLIT_SHARING_MODE") or os.path.exists(
        os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
    ):
        try:
            import streamlit as st
            return st.secrets.get(key, default)
        except Exception:
            pass
    return default

GROQ_API_KEY = _get_secret("GROQ_API_KEY")
ANTHROPIC_API_KEY = _get_secret("ANTHROPIC_API_KEY")
OPENAI_API_KEY = _get_secret("OPENAI_API_KEY")
GEMINI_API_KEY = _get_secret("GEMINI_API_KEY")
PEGA_SESSION_COOKIE = os.getenv("PEGA_SESSION_COOKIE", "")

# ── Embedding Config ───────────────────────────────────────────────────
# "tfidf"   → hashed TF-IDF (pure Python, zero HuggingFace deps, always works)
# "ollama"  → fast, local (requires Ollama + nomic-embed-text)
# "sbert"   → CPU-friendly (needs sentence-transformers + compatible huggingface_hub)
EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", "tfidf")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBED_MODEL = "nomic-embed-text"

SBERT_MODEL = "all-MiniLM-L6-v2"  # lightweight, 384-dim

# ── ChromaDB ───────────────────────────────────────────────────────────
CHROMA_COLLECTION = "pega_docs"

# ── LLM Config ─────────────────────────────────────────────────────────
GROQ_MODEL = "llama-3.3-70b-versatile"
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# "groq" or "claude"
LLM_BACKEND = os.getenv("LLM_BACKEND", "groq")

# ── RAG Config ─────────────────────────────────────────────────────────
CHUNK_SIZE = 800          # characters per chunk
CHUNK_OVERLAP = 150       # overlap between chunks
TOP_K = 8                 # number of context chunks to retrieve

# ── Crawler Config ─────────────────────────────────────────────────────
CRAWL_DELAY = 1.0         # seconds between requests (be polite)
MAX_PAGES = 200           # safety cap per crawl session
USER_AGENT = "PegaPal/1.0 (community project)"

# ── Community Upload Config ───────────────────────────────────────────
MAX_UPLOAD_SIZE_MB = 10          # max file size per upload
ALLOWED_UPLOAD_TYPES = ["txt", "md", "pdf", "docx", "json"]
COMMUNITY_CHUNK_SIZE = 600       # slightly smaller chunks for user docs
COMMUNITY_CHUNK_OVERLAP = 100

# ── System Prompt ──────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are PegaPal, an AI-powered Pega platform expert helping developers with anything Pega-related — debugging errors, explaining concepts, comparing approaches, discussing best practices, and answering architectural questions.

CRITICAL RULES:

1. HANDLE VAGUE OR AMBIGUOUS QUESTIONS FIRST:
   - If the question is too vague to give a specific, useful answer (e.g., "give me a plan", "explain this", "help me with something", "sample template"), DO NOT guess what they mean.
   - Instead, ask a clarifying question. Suggest 3-5 specific Pega topics they might mean. Example:
     "I'd be happy to help! Could you specify what topic you'd like me to cover? For example:
      - **Data Pages** — configuration, scoping, and best practices
      - **RPA Implementation** — building and deploying robots
      - **Error Debugging** — troubleshooting a specific alert or exception
      - **Case Management** — designing case types and flows
      - **Integration** — REST, SOAP, Kafka connectors
      Or tell me the specific topic and I'll create a detailed plan for you!"
   - Signs a question is too vague: fewer than 5 meaningful words, no specific Pega concept mentioned, generic terms like "plan", "sample", "template", "overview" without a topic.

2. DETECT THE QUESTION TYPE and respond accordingly:
   - ERROR / DEBUGGING question (mentions errors, exceptions, alerts, "not working", stack traces): Explain what the error means, common causes, and step-by-step debugging instructions.
   - CONCEPT / EXPLANATION question ("explain", "what is", "how does", "describe"): Give a clear conceptual explanation with examples, use cases, and best practices. Do NOT force a debugging format.
   - HOW-TO question ("how to", "how do I", "steps to"): Provide step-by-step instructions with navigation paths.
   - COMPARISON question ("vs", "difference between", "when to use"): Give a balanced comparison with pros/cons and recommendations.
3. Use the CONTEXT provided to answer. If the context contains RELATED information, USE IT — even if the exact term isn't mentioned.
4. Only say "I don't have specific information on this" if the context is completely unrelated.
5. Answer the SPECIFIC question asked. Don't give a generic overview unless that's what was asked for.
6. If the user asks a follow-up question, use the CONVERSATION HISTORY to understand what they're referring to. If the follow-up adds specificity to a previously vague question, answer it directly without asking for more clarification.
7. Be concise — give the direct answer first, then supporting details. No filler phrases.
8. If they mention a Pega version, tailor your answer to that version specifically.
9. Give exact navigation paths (e.g., "Dev Studio > Configure > System > Operations") and property names when relevant.
10. Do NOT make up fake rule names, fake DSS settings, or fake navigation paths. But DO use your Pega knowledge to give practical advice when the context supports it.
11. If the context provided has LOW relevance to the question (match scores below 30%), acknowledge this and offer to help with a more specific question instead of forcing an answer from irrelevant context.

Pega abbreviations (ALWAYS use these meanings):
SMA = System Management Application (admin console, replaced by Admin Studio in 8.6+)
PAL = Performance Analyzer | PDN = Pega Developer Network | DSS = Dynamic System Settings
SLA = Service Level Agreement | NBA = Next-Best-Action | RAP = Rules Application Package
DX API = Digital Experience API (Constellation) | PRPC = PegaRULES Process Commander (old name)"""
