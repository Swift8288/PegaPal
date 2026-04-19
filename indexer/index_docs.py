"""
ChromaDB Indexer — Chunks, embeds, and stores Pega docs.
Supports multiple embedding backends:
  - "tfidf"   → TF-IDF via sklearn (pure Python, no HuggingFace deps)
  - "ollama"  → local Ollama server with nomic-embed-text (fast, GPU)
  - "sbert"   → sentence-transformers all-MiniLM-L6-v2 (if compatible)
"""

import json
import logging
import re
import hashlib
import math
from collections import Counter
from pathlib import Path
from typing import Optional

import chromadb

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import (
    CHROMA_COLLECTION,
    CHROMA_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_BACKEND,
    IDF_FILE,
    OLLAMA_BASE_URL,
    OLLAMA_EMBED_MODEL,
    RAW_DOCS_DIR,
    SBERT_MODEL,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ── Embedding Backends ─────────────────────────────────────────────────

class TFIDFEmbedder:
    """
    Pure-Python TF-IDF embedder with proper IDF weighting and bigrams.
    No HuggingFace, no sentence-transformers, no version conflicts.

    How it works:
    1. Tokenizes text into unigrams + bigrams (e.g. "data", "page", "data_page")
    2. Computes TF (log-normalized term frequency) for each token
    3. Multiplies by IDF (inverse document frequency) — rare terms score higher
    4. Hashes each token to a fixed-dimension vector using the hashing trick
    5. L2-normalizes the final vector for cosine similarity

    IDF is pre-computed from the entire KB during indexing and saved to disk.
    At query time, IDF is loaded from disk for consistent weighting.
    """

    # Common English stop words to skip (they add noise, not signal)
    STOP_WORDS = frozenset([
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "must",
        "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
        "into", "through", "during", "before", "after", "above", "below",
        "between", "out", "off", "over", "under", "again", "further", "then",
        "once", "here", "there", "when", "where", "why", "how", "all", "each",
        "every", "both", "few", "more", "most", "other", "some", "such", "no",
        "nor", "not", "only", "own", "same", "so", "than", "too", "very",
        "and", "but", "or", "if", "because", "while", "although", "this",
        "that", "these", "those", "it", "its", "what", "which", "who", "whom",
        "i", "me", "my", "we", "our", "you", "your", "he", "him", "his",
        "she", "her", "they", "them", "their", "about", "up", "also", "just",
    ])

    def __init__(self, dim: int = 384):
        self.dim = dim
        self.idf = {}           # token → IDF weight
        self.doc_count = 0      # total number of documents used to build IDF
        self._load_idf()

    def _load_idf(self):
        """Load pre-computed IDF weights from disk if available."""
        if IDF_FILE.exists():
            try:
                with open(IDF_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.idf = data.get("idf", {})
                self.doc_count = data.get("doc_count", 0)
                logger.info(f"Loaded IDF weights: {len(self.idf)} terms from {self.doc_count} docs")
            except Exception as e:
                logger.warning(f"Failed to load IDF file: {e}")

    def save_idf(self):
        """Save IDF weights to disk."""
        IDF_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(IDF_FILE, "w", encoding="utf-8") as f:
            json.dump({"idf": self.idf, "doc_count": self.doc_count}, f)
        logger.info(f"Saved IDF weights: {len(self.idf)} terms, {self.doc_count} docs")

    def build_idf(self, texts: list[str]):
        """
        Compute IDF weights from a corpus of text chunks.
        IDF(t) = log(N / (1 + df(t))) where:
          N = total number of documents
          df(t) = number of documents containing term t
        """
        self.doc_count = len(texts)
        doc_freq = Counter()

        for text in texts:
            # Count each unique token once per document (for document frequency)
            unique_tokens = set(self._tokenize(text))
            for token in unique_tokens:
                doc_freq[token] += 1

        # Compute IDF
        self.idf = {}
        for token, df in doc_freq.items():
            self.idf[token] = math.log(self.doc_count / (1 + df))

        logger.info(
            f"Built IDF from {self.doc_count} chunks — "
            f"{len(self.idf)} unique terms, "
            f"top IDF: {sorted(self.idf.items(), key=lambda x: -x[1])[:5]}"
        )
        self.save_idf()

    def _tokenize(self, text: str) -> list[str]:
        """
        Tokenizer that produces unigrams + bigrams.
        Preserves Pega-specific terms (PEGA0001, Obj-Save, Obj-Browse, etc.).
        Filters stop words from unigrams (but keeps them in bigrams for context).
        """
        text_lower = text.lower()

        # Extract raw tokens: alphanumeric, hyphens, underscores
        raw_tokens = re.findall(r"[a-z0-9][\w\-]*[a-z0-9]|[a-z0-9]+", text_lower)

        # Also extract PEGA alert codes in their canonical form (case-preserved)
        pega_codes = re.findall(r"pega\d{4}", text_lower)

        # Build unigrams (skip stop words)
        unigrams = []
        for t in raw_tokens:
            if t not in self.STOP_WORDS:
                unigrams.append(t)

        # Build bigrams from consecutive raw tokens (including stop words for context)
        bigrams = []
        for i in range(len(raw_tokens) - 1):
            bigram = f"{raw_tokens[i]}_{raw_tokens[i+1]}"
            bigrams.append(bigram)

        # Combine: unigrams + bigrams + PEGA codes (ensure codes are present)
        tokens = unigrams + bigrams + pega_codes
        return tokens

    def _hash_token(self, token: str) -> int:
        """Hash a token to a dimension index."""
        return int(hashlib.md5(token.encode()).hexdigest(), 16) % self.dim

    def _hash_sign(self, token: str) -> int:
        """Hash a token to +1 or -1 for sign hashing (reduces collisions)."""
        return 1 if int(hashlib.sha1(token.encode()).hexdigest(), 16) % 2 == 0 else -1

    def _default_idf(self, token: str) -> float:
        """
        Estimate IDF for tokens not seen during training.
        Rare/specific tokens (identifiers, error codes) get high IDF.
        Common short tokens get low IDF.
        """
        # PEGA alert codes — very specific, high IDF
        if re.match(r"pega\d{4}", token):
            return math.log(max(self.doc_count, 100) / 2)
        # Bigrams — moderately specific
        if "_" in token:
            return math.log(max(self.doc_count, 100) / 5)
        # Technical-looking tokens (has digits, long, etc.)
        if any(c.isdigit() for c in token) or len(token) > 12:
            return math.log(max(self.doc_count, 100) / 3)
        # Unknown short word — assume moderately common
        return math.log(max(self.doc_count, 100) / 20)

    def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Produce fixed-dimension embeddings using proper TF-IDF with hashing.
        """
        embeddings = []
        for text in texts:
            tokens = self._tokenize(text)
            if not tokens:
                embeddings.append([0.0] * self.dim)
                continue

            # Term frequency (log-normalized)
            tf = Counter(tokens)

            # Build vector using hashing trick with TF-IDF weighting
            vec = [0.0] * self.dim
            for token, count in tf.items():
                idx = self._hash_token(token)
                sign = self._hash_sign(token)

                # TF: log-normalized
                tf_weight = 1 + math.log(count)

                # IDF: from pre-computed weights, or estimated for unseen tokens
                idf_weight = self.idf.get(token, self._default_idf(token))

                # TF-IDF
                weight = tf_weight * max(idf_weight, 0.1)  # floor at 0.1 to avoid zeroing out
                vec[idx] += sign * weight

            # L2 normalize
            norm = math.sqrt(sum(v * v for v in vec))
            if norm > 0:
                vec = [v / norm for v in vec]

            embeddings.append(vec)
        return embeddings


class OllamaEmbedder:
    """Embeds text via local Ollama server."""

    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_EMBED_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def embed(self, texts: list[str]) -> list[list[float]]:
        import requests
        embeddings = []
        for text in texts:
            resp = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=30,
            )
            resp.raise_for_status()
            embeddings.append(resp.json()["embedding"])
        return embeddings


class SBERTEmbedder:
    """Embeds text via sentence-transformers (CPU-friendly)."""

    def __init__(self, model_name: str = SBERT_MODEL):
        from sentence_transformers import SentenceTransformer
        logger.info(f"Loading sentence-transformer model: {model_name}")
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, show_progress_bar=False).tolist()


def get_embedder(backend: Optional[str] = None):
    """Factory: return the configured embedding backend."""
    backend = backend or EMBEDDING_BACKEND
    if backend == "ollama":
        return OllamaEmbedder()
    elif backend == "sbert":
        return SBERTEmbedder()
    # Default: TF-IDF (zero external deps, always works)
    logger.info("Using TF-IDF hashed embeddings (no HuggingFace deps)")
    return TFIDFEmbedder()


# ── Chunking ───────────────────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping chunks.
    Tries to break on paragraph/sentence boundaries first.
    """
    if not text or len(text) <= chunk_size:
        return [text] if text else []

    # Split on double newlines (paragraphs) first
    paragraphs = re.split(r"\n\n+", text)
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= chunk_size:
            current = f"{current}\n\n{para}" if current else para
        else:
            if current:
                chunks.append(current.strip())
            # If a single paragraph exceeds chunk_size, split it further
            if len(para) > chunk_size:
                words = para.split()
                current = ""
                for word in words:
                    if len(current) + len(word) + 1 <= chunk_size:
                        current = f"{current} {word}" if current else word
                    else:
                        if current:
                            chunks.append(current.strip())
                        current = word
            else:
                current = para

    if current:
        chunks.append(current.strip())

    # Add overlap: prepend tail of previous chunk to each chunk
    if overlap > 0 and len(chunks) > 1:
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_tail = chunks[i - 1][-overlap:]
            overlapped.append(f"{prev_tail}... {chunks[i]}")
        chunks = overlapped

    return chunks


# ── Indexing ───────────────────────────────────────────────────────────

class _NoOpEmbeddingFunction:
    """Dummy embedding function to prevent ChromaDB from loading sentence-transformers."""
    def __call__(self, input):
        return [[0.0] * 384 for _ in input]

    def name(self):
        return "noop"


class PegaIndexer:
    """Chunks docs, computes embeddings, and stores in ChromaDB."""

    def __init__(self, backend: Optional[str] = None):
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        try:
            self._open_chroma()
        except Exception as e:
            # ChromaDB version mismatch — delete and rebuild from raw docs
            logger.warning(f"ChromaDB open failed ({e}), will rebuild from scratch...")
            import shutil
            if CHROMA_DIR.exists():
                shutil.rmtree(CHROMA_DIR)
            CHROMA_DIR.mkdir(parents=True, exist_ok=True)
            self._open_chroma()

        self.embedder = get_embedder(backend)

        # Auto-rebuild if collection is empty (e.g. fresh /tmp on Streamlit Cloud)
        count = self.collection.count()
        if count == 0 and RAW_DOCS_DIR.exists():
            logger.info("Collection empty — auto-indexing from raw docs...")
            total = self.index_directory(RAW_DOCS_DIR)
            logger.info(f"Auto-rebuilt index: {total} chunks from raw docs")
        else:
            logger.info(
                f"Indexer ready — collection '{CHROMA_COLLECTION}' "
                f"({count} existing docs), "
                f"backend={backend or EMBEDDING_BACKEND}"
            )

    def _open_chroma(self):
        """Open ChromaDB client and collection."""
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = self.client.get_or_create_collection(
            name=CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"},
            embedding_function=_NoOpEmbeddingFunction(),
        )
        # Test that the DB actually works (catches schema mismatches)
        self.collection.count()

    def index_document(self, doc: dict) -> int:
        """
        Index a single document (dict with 'url', 'title', 'content').
        Returns number of chunks added.

        Documents are stored in lowercase for case-insensitive keyword search.
        Original text is preserved in metadata['original_text'] for display.
        """
        chunks = chunk_text(doc["content"])
        if not chunks:
            return 0

        ids = [f"{doc['url']}::chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "url": doc["url"],
                "title": doc.get("title", ""),
                "chunk_index": i,
                "original_text": chunk,  # preserve original case for display
            }
            for i, chunk in enumerate(chunks)
        ]

        embeddings = self.embedder.embed(chunks)

        # Store lowercase documents for case-insensitive $contains search
        lowercase_chunks = [c.lower() for c in chunks]

        self.collection.upsert(
            ids=ids,
            documents=lowercase_chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return len(chunks)

    @staticmethod
    def _normalize_doc(raw: dict, filename: str) -> list[dict]:
        """
        Convert any JSON KB format into a list of indexable docs
        (each with 'url', 'title', 'content').

        Supports two formats:
          1. Legacy: {'url', 'title', 'content'} — passed through as-is.
          2. Topics/QA: {'title', 'topics': [...], 'qa_pairs': [...]}
             — each topic becomes a separate doc, QA pairs become one doc.
        """
        # Legacy format — already has 'content'
        if "content" in raw:
            if "url" not in raw:
                raw["url"] = f"kb://{filename}"
            return [raw]

        # Topics + QA pairs format (from official PDF extractions)
        docs = []
        base_title = raw.get("title", filename)
        source = raw.get("source", "")
        version = raw.get("version", "")

        # Each topic becomes a separate indexable document
        for i, topic in enumerate(raw.get("topics", [])):
            topic_name = topic.get("topic", f"Topic {i+1}")
            content = topic.get("content", "")
            if content:
                header = f"{base_title} — {topic_name}"
                if version:
                    header += f" ({version})"
                docs.append({
                    "url": f"kb://{filename}#topic-{i}",
                    "title": header,
                    "content": f"{topic_name}\n\n{content}",
                })

        # QA pairs as a combined document
        qa_pairs = raw.get("qa_pairs", [])
        if qa_pairs:
            qa_content_parts = []
            for qa in qa_pairs:
                q = qa.get("question", "")
                a = qa.get("answer", "")
                if q and a:
                    qa_content_parts.append(f"Q: {q}\nA: {a}")
            if qa_content_parts:
                docs.append({
                    "url": f"kb://{filename}#qa",
                    "title": f"{base_title} — Q&A",
                    "content": "\n\n".join(qa_content_parts),
                })

        return docs

    def index_directory(self, docs_dir: Path = RAW_DOCS_DIR) -> int:
        """
        Index all JSON doc files in a directory. Returns total chunks.
        For TF-IDF backend: computes IDF weights from ALL chunks first,
        then embeds and indexes. This ensures IDF is accurate.
        """
        json_files = sorted(docs_dir.glob("*.json"))
        if not json_files:
            logger.warning(f"No JSON files found in {docs_dir}")
            return 0

        # ── Pass 1: Read all docs and chunk them (for IDF computation) ──
        all_docs = []  # list of (doc_dict, source_file)
        all_chunks_flat = []  # all chunk texts for IDF
        for jf in json_files:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Normalize: handle both list and single-doc formats
            raw_list = data if isinstance(data, list) else [data]
            docs = []
            for raw in raw_list:
                docs.extend(self._normalize_doc(raw, jf.stem))
            for doc in docs:
                chunks = chunk_text(doc["content"])
                all_docs.append((doc, chunks, jf.name))
                all_chunks_flat.extend(chunks)

        logger.info(f"Pass 1: {len(all_docs)} docs → {len(all_chunks_flat)} total chunks")

        # ── Build IDF from all chunks (TF-IDF backend only) ──
        if isinstance(self.embedder, TFIDFEmbedder):
            logger.info("Building IDF weights from full corpus...")
            self.embedder.build_idf(all_chunks_flat)

        # ── Pass 2: Embed and index each document ──
        # Store lowercase documents for case-insensitive keyword search.
        # Original text preserved in metadata for display.
        total_chunks = 0
        for doc, chunks, filename in all_docs:
            if not chunks:
                continue

            ids = [f"{doc['url']}::chunk_{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    "url": doc["url"],
                    "title": doc.get("title", ""),
                    "chunk_index": i,
                    "original_text": chunk,
                }
                for i, chunk in enumerate(chunks)
            ]
            embeddings = self.embedder.embed(chunks)
            lowercase_chunks = [c.lower() for c in chunks]

            self.collection.upsert(
                ids=ids,
                documents=lowercase_chunks,
                embeddings=embeddings,
                metadatas=metadatas,
            )
            total_chunks += len(chunks)

        logger.info(f"Indexing complete — {total_chunks} total chunks from {len(json_files)} files")
        return total_chunks

    def _build_title_vocab(self):
        """
        Build a vocabulary of searchable terms from all indexed document titles.
        Called once and cached. This means ANY new KB document's title terms
        are automatically searchable — no hardcoded patterns needed.
        """
        if hasattr(self, '_title_vocab') and self._title_vocab:
            return self._title_vocab

        # Common English stop words to exclude
        stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can',
            'that', 'this', 'these', 'those', 'it', 'its',
            'not', 'no', 'nor', 'as', 'if', 'then', 'than', 'too', 'very',
            'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
            'some', 'such', 'only', 'own', 'same', 'so', 'about', 'up',
            'out', 'how', 'what', 'which', 'who', 'whom', 'why', 'where',
            'when', 'here', 'there', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'under', 'over',
            'completing', 'configuring', 'creating', 'using', 'working',
            'managing', 'defining', 'adding', 'setting', 'complete', 'guide',
            'overview', 'introduction', 'getting', 'started', 'tab', 'form',
            'page', 'new', 'pega', 'platform',
        }

        title_terms = set()
        try:
            # Get all unique titles from the collection metadata
            results = self.collection.get(include=["metadatas"], limit=10000)
            for meta in results.get("metadatas", []):
                title = meta.get("title", "")
                # Extract meaningful words (3+ chars, not stop words)
                words = re.findall(r'[a-zA-Z]{3,}', title)
                for word in words:
                    if word.lower() not in stop_words and len(word) >= 4:
                        title_terms.add(word.lower())

                # Also extract multi-word phrases from titles (bigrams)
                title_lower = title.lower()
                # Extract "Word Word" patterns as phrases
                bigrams = re.findall(r'[a-z]{3,}\s+[a-z]{3,}', title_lower)
                for bg in bigrams:
                    parts = bg.split()
                    if parts[0] not in stop_words and parts[1] not in stop_words:
                        title_terms.add(bg)
        except Exception as e:
            logger.debug(f"Title vocab build: {e}")

        self._title_vocab = title_terms
        logger.info(f"Built title vocabulary: {len(title_terms)} searchable terms")
        return self._title_vocab

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Hybrid search: keyword filter + vector search, merged and ranked.

        Ranking tiers:
          - Title match (keyword found in document title): distance = 0.05
          - Content match (keyword found in chunk text):   distance = 0.25
          - Vector match (TF-IDF cosine similarity):       actual distance

        Keywords are extracted automatically from:
          1. PEGA alert codes (PEGA0001, etc.)
          2. Technical patterns (CamelCase, abbreviations, hyphenated terms)
          3. ANY word that appears in indexed document titles — this means
             new KB documents are automatically searchable without code changes.
        """
        hits = []
        seen_ids = set()
        query_upper = query.upper()

        # ── Step 1: Extract keywords worth filtering on ──
        # PEGA alert codes (PEGA0001, PEGA0045, etc.)
        alert_codes = re.findall(r'PEGA\d{4}', query_upper)
        # Known Pega abbreviations
        pega_abbrevs = re.findall(
            r'\b(?:DSS|SMA|PAL|PDN|SLA|NBA|RAP|PRPC|PDC|DX\s*API|FIPS|CSP|CRUD|BIX|OLAP)\b', query_upper
        )
        # Technical terms: CamelCase identifiers (NullPointerException, IndexOutOfBounds)
        camel_case = re.findall(r'[A-Z][a-z]+(?:[A-Z][a-z]+)+', query)
        # Hyphenated Pega terms (Obj-Save, Obj-Browse, next-best-action)
        hyphenated = re.findall(r'[A-Za-z]+-[A-Za-z]+', query)

        # ── Auto-keyword extraction from document titles ──
        # Match any query word (4+ chars) that appears in KB document titles.
        # This means "blueprint", "autopilot", "constellation", "cassandra",
        # etc. are ALL automatically searchable because they appear in titles.
        title_vocab = self._build_title_vocab()
        query_lower = query.lower()
        query_words = re.findall(r'[a-z]{4,}', query_lower)
        auto_keywords = [w for w in query_words if w in title_vocab]

        # Also match multi-word phrases from the query against title bigrams
        for bigram in title_vocab:
            if ' ' in bigram and bigram in query_lower:
                auto_keywords.append(bigram)

        keyword_terms = list(set(
            alert_codes + pega_abbrevs + camel_case + hyphenated + auto_keywords
        ))

        # ── Step 2: Keyword-filtered search ──
        # Documents are stored in lowercase, so we only need one lowercase search per term.
        if keyword_terms:
            query_embedding = self.embedder.embed([query])[0]
            for term in keyword_terms:
                search_term = term.lower()
                try:
                    kw_results = self.collection.query(
                        query_embeddings=[query_embedding],
                        n_results=top_k * 2,  # fetch more to find title matches
                        where_document={"$contains": search_term},
                        include=["documents", "metadatas", "distances"],
                    )
                    for i in range(len(kw_results["ids"][0])):
                        doc_id = kw_results["ids"][0][i]
                        if doc_id in seen_ids:
                            continue
                        seen_ids.add(doc_id)

                        title = kw_results["metadatas"][0][i].get("title", "")
                        # Title match = highest priority
                        if search_term in title.lower():
                            boost_dist = 0.05
                        else:
                            boost_dist = 0.25

                        hits.append({
                            "id": doc_id,
                            "document": kw_results["documents"][0][i],
                            "metadata": kw_results["metadatas"][0][i],
                            "distance": boost_dist,
                        })
                except Exception as e:
                    logger.debug(f"Keyword filter for '{search_term}': {e}")

        # ── Step 3: Standard vector search to fill remaining slots ──
        query_embedding = self.embedder.embed([query])[0]
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 2,
            include=["documents", "metadatas", "distances"],
        )
        for i in range(len(results["ids"][0])):
            doc_id = results["ids"][0][i]
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                hits.append({
                    "id": doc_id,
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                })

        # Sort by distance (best matches first) and return top_k
        hits.sort(key=lambda h: h["distance"])
        final = hits[:top_k]

        # Restore original-case text for LLM context (stored in metadata)
        for hit in final:
            original = hit["metadata"].get("original_text")
            if original:
                hit["document"] = original

        return final

    def stats(self) -> dict:
        """Return collection statistics."""
        return {
            "collection": CHROMA_COLLECTION,
            "total_chunks": self.collection.count(),
            "backend": EMBEDDING_BACKEND,
        }

    def rebuild_index(self, docs_dir: Path = RAW_DOCS_DIR) -> int:
        """
        Clear the entire collection and re-index from scratch.
        Use this after changing the embedding algorithm (e.g. adding IDF).
        """
        logger.info("🔄 Rebuilding index from scratch...")
        # Delete existing collection and recreate
        try:
            self.client.delete_collection(CHROMA_COLLECTION)
            logger.info("Deleted existing collection")
        except Exception:
            pass

        self.collection = self.client.get_or_create_collection(
            name=CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"},
            embedding_function=_NoOpEmbeddingFunction(),
        )

        # Delete old IDF file so it's rebuilt fresh
        if IDF_FILE.exists():
            IDF_FILE.unlink()
            logger.info("Deleted old IDF file")

        # Re-index
        total = self.index_directory(docs_dir)

        # Also re-index community docs if they exist
        from config import COMMUNITY_DOCS_DIR
        if COMMUNITY_DOCS_DIR.exists():
            community_jsons = list(COMMUNITY_DOCS_DIR.glob("*.json"))
            if community_jsons:
                logger.info(f"Re-indexing {len(community_jsons)} community docs...")
                for jf in community_jsons:
                    try:
                        with open(jf, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        docs = data if isinstance(data, list) else [data]
                        for doc in docs:
                            self.index_document(doc)
                    except Exception as e:
                        logger.warning(f"Failed to re-index {jf.name}: {e}")

        logger.info(f"✅ Rebuild complete — {self.collection.count()} total chunks")
        return self.collection.count()


# ── Convenience functions ──────────────────────────────────────────────

def add_to_kb(url: str, backend: Optional[str] = None) -> int:
    """
    One-liner: crawl a URL → chunk → embed → store.
    Returns number of chunks added.
    """
    from crawler.scraper import add_url

    doc = add_url(url)
    if not doc:
        logger.error(f"Failed to crawl: {url}")
        return 0

    indexer = PegaIndexer(backend=backend)
    return indexer.index_document(doc)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="PegaPal KB Indexer")
    parser.add_argument("--rebuild", action="store_true",
                        help="Clear and rebuild the entire index (use after embedding changes)")
    args = parser.parse_args()

    indexer = PegaIndexer()

    if args.rebuild:
        total = indexer.rebuild_index()
        print(f"\n✅ Rebuilt index: {total} chunks")
    else:
        total = indexer.index_directory()
        print(f"\nDone! {total} chunks indexed.")

    print(f"Stats: {indexer.stats()}")
