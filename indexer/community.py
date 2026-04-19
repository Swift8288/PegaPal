"""
PegaPal — Community Document Upload & Indexer
Handles user-uploaded documents: parse, chunk, embed, store in ChromaDB.
Supports: TXT, MD, PDF, DOCX, JSON
Includes security scanning and approval workflow:
  Upload → Security Scan → Pending Queue → Admin Approve → Index to ChromaDB
"""

import json
import logging
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import (
    CHROMA_COLLECTION,
    CHROMA_DIR,
    COMMUNITY_CHUNK_OVERLAP,
    COMMUNITY_CHUNK_SIZE,
    COMMUNITY_DOCS_DIR,
    COMMUNITY_META_FILE,
    EMBEDDING_BACKEND,
)
from indexer.index_docs import PegaIndexer, chunk_text
from indexer.security import get_scanner

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ── File Parsers ──────────────────────────────────────────────────────

def parse_txt(file_bytes: bytes, filename: str) -> str:
    """Parse plain text or markdown files."""
    return file_bytes.decode("utf-8", errors="replace")


def parse_pdf(file_bytes: bytes, filename: str) -> str:
    """Parse PDF files using PyPDF2 (lightweight) or pdfplumber."""
    try:
        import pdfplumber
        import io
        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n\n".join(text_parts)
    except ImportError:
        pass

    try:
        from PyPDF2 import PdfReader
        import io
        reader = PdfReader(io.BytesIO(file_bytes))
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n\n".join(text_parts)
    except ImportError:
        logger.warning("No PDF library available. Install pdfplumber or PyPDF2.")
        return ""


def parse_docx(file_bytes: bytes, filename: str) -> str:
    """Parse Word documents using python-docx."""
    try:
        from docx import Document
        import io
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)
    except ImportError:
        logger.warning("python-docx not installed. Install with: pip install python-docx")
        return ""


def parse_json(file_bytes: bytes, filename: str) -> str:
    """Parse JSON files — expects {title, content} or {url, title, content} format."""
    try:
        data = json.loads(file_bytes.decode("utf-8", errors="replace"))
        if isinstance(data, dict):
            return data.get("content", "") or json.dumps(data, indent=2)
        elif isinstance(data, list):
            parts = []
            for item in data:
                if isinstance(item, dict):
                    parts.append(item.get("content", "") or json.dumps(item))
                else:
                    parts.append(str(item))
            return "\n\n".join(parts)
        return str(data)
    except json.JSONDecodeError:
        return file_bytes.decode("utf-8", errors="replace")


PARSERS = {
    ".txt": parse_txt,
    ".md": parse_txt,
    ".pdf": parse_pdf,
    ".docx": parse_docx,
    ".json": parse_json,
}


# ── Community Metadata Tracker ────────────────────────────────────────

class CommunityTracker:
    """
    Tracks uploaded documents: who uploaded, when, file info, chunk counts.
    Stored in a JSON file for persistence.
    """

    def __init__(self, meta_file: Path = COMMUNITY_META_FILE):
        self.meta_file = meta_file
        self.meta_file.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    def _load(self) -> dict:
        if self.meta_file.exists():
            try:
                with open(self.meta_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Migration: add pending_uploads if missing (existing installs)
                if "pending_uploads" not in data:
                    data["pending_uploads"] = []
                if "rejected_uploads" not in data:
                    data["rejected_uploads"] = []
                return data
            except (json.JSONDecodeError, IOError):
                pass
        return {
            "uploads": [],          # approved & indexed docs
            "pending_uploads": [],   # awaiting admin review
            "rejected_uploads": [],  # rejected by admin
            "total_docs": 0,
            "total_chunks": 0,
            "contributors": {},
            "last_refresh": None,
        }

    def _save(self):
        with open(self.meta_file, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, default=str)

    def record_pending(self, filename: str, contributor: str,
                       file_size: int, doc_id: str, scan_warnings: list = None):
        """Record a new upload as pending (awaiting admin approval)."""
        entry = {
            "filename": filename,
            "contributor": contributor,
            "file_size": file_size,
            "doc_id": doc_id,
            "uploaded_at": datetime.now().isoformat(),
            "status": "pending",
            "scan_warnings": scan_warnings or [],
        }
        self._data["pending_uploads"].append(entry)
        self._save()
        return entry

    def approve_upload(self, doc_id: str, chunks: int):
        """Move a pending upload to approved status and index it."""
        pending = [u for u in self._data["pending_uploads"] if u["doc_id"] == doc_id]
        if not pending:
            return None

        entry = pending[0]
        entry["status"] = "approved"
        entry["approved_at"] = datetime.now().isoformat()
        entry["chunks"] = chunks

        # Move from pending to approved uploads
        self._data["pending_uploads"] = [
            u for u in self._data["pending_uploads"] if u["doc_id"] != doc_id
        ]
        self._data["uploads"].append(entry)
        self._data["total_docs"] += 1
        self._data["total_chunks"] += chunks

        # Track contributor stats
        contributor = entry.get("contributor", "anonymous")
        if contributor not in self._data["contributors"]:
            self._data["contributors"][contributor] = {"docs": 0, "chunks": 0}
        self._data["contributors"][contributor]["docs"] += 1
        self._data["contributors"][contributor]["chunks"] += chunks

        self._save()
        return entry

    def reject_upload(self, doc_id: str, reason: str = ""):
        """Reject a pending upload."""
        pending = [u for u in self._data["pending_uploads"] if u["doc_id"] == doc_id]
        if not pending:
            return None

        entry = pending[0]
        entry["status"] = "rejected"
        entry["rejected_at"] = datetime.now().isoformat()
        entry["reject_reason"] = reason

        # Move from pending to rejected
        self._data["pending_uploads"] = [
            u for u in self._data["pending_uploads"] if u["doc_id"] != doc_id
        ]
        self._data["rejected_uploads"].append(entry)
        self._save()
        return entry

    def get_pending_uploads(self) -> list:
        """Get all pending uploads awaiting review."""
        return list(self._data.get("pending_uploads", []))

    def get_pending_count(self) -> int:
        """Get count of pending uploads."""
        return len(self._data.get("pending_uploads", []))

    def record_upload(self, filename: str, contributor: str, chunks: int,
                      file_size: int, doc_id: str):
        """Record a directly approved upload (legacy / auto-approve path)."""
        entry = {
            "filename": filename,
            "contributor": contributor,
            "chunks": chunks,
            "file_size": file_size,
            "doc_id": doc_id,
            "uploaded_at": datetime.now().isoformat(),
            "status": "approved",
        }
        self._data["uploads"].append(entry)
        self._data["total_docs"] += 1
        self._data["total_chunks"] += chunks

        # Track contributor stats
        if contributor not in self._data["contributors"]:
            self._data["contributors"][contributor] = {"docs": 0, "chunks": 0}
        self._data["contributors"][contributor]["docs"] += 1
        self._data["contributors"][contributor]["chunks"] += chunks

        self._save()
        return entry

    def get_stats(self) -> dict:
        return {
            "total_docs": self._data["total_docs"],
            "total_chunks": self._data["total_chunks"],
            "num_contributors": len(self._data["contributors"]),
            "pending_count": len(self._data.get("pending_uploads", [])),
            "rejected_count": len(self._data.get("rejected_uploads", [])),
            "last_refresh": self._data.get("last_refresh"),
        }

    def get_recent_uploads(self, limit: int = 10) -> list:
        return self._data["uploads"][-limit:][::-1]

    def get_top_contributors(self, limit: int = 5) -> list:
        contributors = self._data.get("contributors", {})
        sorted_c = sorted(contributors.items(), key=lambda x: x[1]["docs"], reverse=True)
        return [{"name": name, **stats} for name, stats in sorted_c[:limit]]

    def get_all_doc_ids(self) -> list:
        return [u["doc_id"] for u in self._data["uploads"]]

    def set_last_refresh(self):
        self._data["last_refresh"] = datetime.now().isoformat()
        self._save()

    def remove_upload(self, doc_id: str):
        """Remove an upload record by doc_id."""
        self._data["uploads"] = [
            u for u in self._data["uploads"] if u["doc_id"] != doc_id
        ]
        self._save()


# ── Community Indexer ─────────────────────────────────────────────────

class CommunityIndexer:
    """
    Handles community document uploads:
    1. Parse uploaded file (TXT/MD/PDF/DOCX/JSON)
    2. Chunk the content
    3. Index into ChromaDB with community metadata
    4. Track in community metadata file
    """

    def __init__(self, indexer: Optional[PegaIndexer] = None):
        self.indexer = indexer or PegaIndexer()
        self.tracker = CommunityTracker()

        # Ensure community docs directory exists
        COMMUNITY_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    def process_upload(
        self,
        file_bytes: bytes,
        filename: str,
        contributor: str = "anonymous",
        title: Optional[str] = None,
        description: str = "",
        session_id: str = "default",
    ) -> dict:
        """
        Process an uploaded file with security scanning and approval queue:
        1. Security scan (magic bytes, dangerous patterns, content quality)
        2. Parse file content
        3. Save raw file + JSON to community_docs/
        4. Add to PENDING queue (NOT indexed yet)

        Docs only get indexed into ChromaDB after admin approval.
        Returns dict with status, scan results, doc_id.
        """
        # ── Step 1: Security Scan ────────────────────────────────────
        scanner = get_scanner()
        scan_result = scanner.scan(file_bytes, filename, session_id=session_id)

        if not scan_result.safe:
            logger.warning(f"Upload REJECTED by security scan: '{filename}' — {scan_result.errors}")
            return {
                "success": False,
                "error": scan_result.errors[0] if scan_result.errors else "Security check failed.",
                "scan_errors": scan_result.errors,
                "rejected_by": "security_scanner",
            }

        # ── Step 2: Parse ────────────────────────────────────────────
        ext = Path(filename).suffix.lower()
        parser = PARSERS.get(ext)
        if not parser:
            return {
                "success": False,
                "error": f"Unsupported file type: {ext}. Supported: {', '.join(PARSERS.keys())}",
            }

        try:
            content = parser(file_bytes, filename)
        except Exception as e:
            return {"success": False, "error": f"Failed to parse {filename}: {str(e)}"}

        if not content or len(content.strip()) < 50:
            return {
                "success": False,
                "error": "File is empty or too short (minimum 50 characters of content).",
            }

        # ── Step 3: Generate unique doc ID ────────────────────────────
        content_hash = hashlib.md5(content.encode()).hexdigest()[:10]
        doc_id = f"community_{int(time.time())}_{content_hash}"
        doc_title = title or Path(filename).stem.replace("_", " ").replace("-", " ").title()

        # ── Step 4: Save raw file for future re-indexing ──────────────
        raw_path = COMMUNITY_DOCS_DIR / f"{doc_id}{ext}"
        with open(raw_path, "wb") as f:
            f.write(file_bytes)

        # Save as JSON for consistent re-indexing
        doc_json = {
            "url": f"community://{doc_id}",
            "title": doc_title,
            "content": content,
            "contributor": contributor,
            "description": description,
            "filename": filename,
            "uploaded_at": datetime.now().isoformat(),
            "status": "pending",
            "file_hash": scan_result.file_hash,
        }
        json_path = COMMUNITY_DOCS_DIR / f"{doc_id}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(doc_json, f, indent=2)

        # ── Step 5: Add to PENDING queue (NOT indexed yet) ────────────
        self.tracker.record_pending(
            filename=filename,
            contributor=contributor,
            file_size=len(file_bytes),
            doc_id=doc_id,
            scan_warnings=scan_result.warnings,
        )

        logger.info(
            f"Community upload QUEUED: '{filename}' by {contributor} "
            f"(hash={scan_result.file_hash}, warnings={len(scan_result.warnings)})"
        )

        return {
            "success": True,
            "status": "pending",
            "doc_id": doc_id,
            "title": doc_title,
            "content_length": len(content),
            "contributor": contributor,
            "scan_warnings": scan_result.warnings,
            "message": "Document passed security scan and is pending admin approval.",
        }

    def approve_document(self, doc_id: str) -> dict:
        """
        Admin approves a pending document → chunk and index into ChromaDB.
        """
        # Load the saved JSON
        json_path = COMMUNITY_DOCS_DIR / f"{doc_id}.json"
        if not json_path.exists():
            return {"success": False, "error": f"Document {doc_id} not found."}

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                doc = json.load(f)
        except Exception as e:
            return {"success": False, "error": f"Failed to read document: {e}"}

        content = doc.get("content", "")
        if not content:
            return {"success": False, "error": "Document has no content."}

        # Chunk with community settings
        chunks = chunk_text(content, COMMUNITY_CHUNK_SIZE, COMMUNITY_CHUNK_OVERLAP)
        if not chunks:
            return {"success": False, "error": "Could not generate chunks from document."}

        # Index into ChromaDB
        doc_title = doc.get("title", "Community Doc")
        contributor = doc.get("contributor", "anonymous")

        ids = [f"{doc_id}::chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "url": doc.get("url", f"community://{doc_id}"),
                "title": doc_title,
                "chunk_index": i,
                "source_type": "community",
                "contributor": contributor,
                "filename": doc.get("filename", "unknown"),
            }
            for i in range(len(chunks))
        ]

        embeddings = self.indexer.embedder.embed(chunks)
        self.indexer.collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        # Update JSON status
        doc["status"] = "approved"
        doc["approved_at"] = datetime.now().isoformat()
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2)

        # Update tracker
        self.tracker.approve_upload(doc_id, chunks=len(chunks))

        logger.info(f"APPROVED: '{doc.get('filename')}' → {len(chunks)} chunks indexed")

        return {
            "success": True,
            "doc_id": doc_id,
            "title": doc_title,
            "chunks": len(chunks),
            "contributor": contributor,
        }

    def reject_document(self, doc_id: str, reason: str = "") -> dict:
        """
        Admin rejects a pending document → remove saved files.
        """
        # Update tracker
        entry = self.tracker.reject_upload(doc_id, reason=reason)
        if not entry:
            return {"success": False, "error": f"Document {doc_id} not found in pending queue."}

        # Remove saved files
        json_path = COMMUNITY_DOCS_DIR / f"{doc_id}.json"
        if json_path.exists():
            json_path.unlink()

        # Find and remove raw file (any extension)
        for raw_file in COMMUNITY_DOCS_DIR.glob(f"{doc_id}.*"):
            if raw_file.suffix != ".json":  # already removed
                raw_file.unlink()

        logger.info(f"REJECTED: '{entry.get('filename')}' — reason: {reason or 'none given'}")

        return {
            "success": True,
            "doc_id": doc_id,
            "filename": entry.get("filename", "unknown"),
            "reason": reason,
        }

    def get_pending_for_review(self) -> list:
        """
        Get pending uploads with content preview for admin review.
        """
        pending = self.tracker.get_pending_uploads()
        review_items = []

        for item in pending:
            doc_id = item["doc_id"]
            json_path = COMMUNITY_DOCS_DIR / f"{doc_id}.json"
            preview = ""
            if json_path.exists():
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        doc = json.load(f)
                    content = doc.get("content", "")
                    preview = content[:500] + ("..." if len(content) > 500 else "")
                except Exception:
                    preview = "[Could not load preview]"

            review_items.append({
                **item,
                "preview": preview,
            })

        return review_items

    def get_stats(self) -> dict:
        """Get community upload statistics."""
        return self.tracker.get_stats()

    def get_recent_uploads(self, limit: int = 10) -> list:
        """Get recent uploads for display."""
        return self.tracker.get_recent_uploads(limit)

    def get_top_contributors(self, limit: int = 5) -> list:
        """Get top contributors by upload count."""
        return self.tracker.get_top_contributors(limit)

    def refresh_all(self) -> dict:
        """
        Re-index all APPROVED community documents from saved JSON files.
        Used for daily refresh or when embedding backend changes.
        Skips pending and rejected docs.
        """
        json_files = sorted(COMMUNITY_DOCS_DIR.glob("*.json"))
        if not json_files:
            return {"refreshed": 0, "chunks": 0}

        total_chunks = 0
        refreshed = 0

        for jf in json_files:
            try:
                with open(jf, "r", encoding="utf-8") as f:
                    doc = json.load(f)

                # Only re-index approved documents
                if doc.get("status") not in ("approved", None):
                    continue

                doc_id = jf.stem
                content = doc.get("content", "")
                if not content:
                    continue

                chunks = chunk_text(content, COMMUNITY_CHUNK_SIZE, COMMUNITY_CHUNK_OVERLAP)
                if not chunks:
                    continue

                ids = [f"{doc_id}::chunk_{i}" for i in range(len(chunks))]
                metadatas = [
                    {
                        "url": doc.get("url", f"community://{doc_id}"),
                        "title": doc.get("title", "Community Doc"),
                        "chunk_index": i,
                        "source_type": "community",
                        "contributor": doc.get("contributor", "anonymous"),
                        "filename": doc.get("filename", jf.name),
                    }
                    for i in range(len(chunks))
                ]

                embeddings = self.indexer.embedder.embed(chunks)
                self.indexer.collection.upsert(
                    ids=ids,
                    documents=chunks,
                    embeddings=embeddings,
                    metadatas=metadatas,
                )

                total_chunks += len(chunks)
                refreshed += 1
                logger.info(f"  Refreshed {jf.name}: {len(chunks)} chunks")

            except Exception as e:
                logger.error(f"  Failed to refresh {jf.name}: {e}")

        self.tracker.set_last_refresh()
        logger.info(f"Community refresh complete — {refreshed} docs, {total_chunks} chunks")

        return {"refreshed": refreshed, "chunks": total_chunks}


if __name__ == "__main__":
    # Test with a sample text file
    ci = CommunityIndexer()
    print("Community stats:", ci.get_stats())
    print("Recent uploads:", ci.get_recent_uploads())
