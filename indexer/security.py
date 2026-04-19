"""
PegaPal — Upload Security Scanner
Validates and sanitizes community-uploaded documents before processing.

Security checks:
1. File type validation (magic bytes, not just extension)
2. File size limits
3. Content sanitization (strip HTML/JS/SQL injection patterns)
4. Rate limiting per session
5. Suspicious pattern detection
6. Content length validation
"""

import re
import logging
import hashlib
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── Magic Bytes for File Type Validation ──────────────────────────────
MAGIC_BYTES = {
    ".pdf": [b"%PDF"],
    ".docx": [b"PK\x03\x04"],  # ZIP-based format
    ".json": None,  # validated by content parsing
    ".txt": None,   # any bytes OK
    ".md": None,    # any bytes OK
}

# ── Dangerous Patterns ────────────────────────────────────────────────
# Patterns that should never appear in legitimate Pega documentation
DANGEROUS_PATTERNS = [
    # Script injection
    r"<script[\s>]",
    r"javascript\s*:",
    r"on(load|error|click|mouseover)\s*=",
    r"eval\s*\(",
    r"document\.(cookie|write|location)",
    r"window\.(location|open)",
    # SQL injection
    r";\s*(DROP|DELETE|UPDATE|INSERT|ALTER)\s+",
    r"UNION\s+SELECT",
    r"'\s*OR\s+'1'\s*=\s*'1",
    # Command injection
    r";\s*(rm|wget|curl|chmod|sudo|bash|sh|nc|netcat)\s",
    r"\$\(.*\)",
    r"`.*`",
    # Base64 encoded executables
    r"TVqQAAMAAAAEAAAA",  # MZ header in base64 (Windows executable)
    # PHP / server-side
    r"<\?php",
    r"<%\s",
    # Encoded attacks
    r"&#x[0-9a-f]+;",  # hex-encoded HTML entities (common in XSS)
]

DANGEROUS_REGEX = [re.compile(p, re.IGNORECASE) for p in DANGEROUS_PATTERNS]

# ── Suspicious Content Patterns ───────────────────────────────────────
# Not necessarily malicious but worth flagging
SUSPICIOUS_PATTERNS = [
    r"(password|passwd|secret|token|api_key)\s*[:=]\s*\S+",
    r"\b\d{16}\b",  # potential credit card numbers
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b.*\b[A-Za-z0-9._%+-]+@",  # multiple emails
]

SUSPICIOUS_REGEX = [re.compile(p, re.IGNORECASE) for p in SUSPICIOUS_PATTERNS]


@dataclass
class ScanResult:
    """Result of a security scan."""
    safe: bool
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    cleaned_content: str = ""
    file_hash: str = ""


class UploadScanner:
    """
    Scans uploaded files for security issues before they enter the pipeline.
    """

    def __init__(self, max_size_mb: int = 10, max_uploads_per_session: int = 10):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_uploads_per_session = max_uploads_per_session
        self._session_uploads: dict[str, int] = {}  # session_id → count

    def scan(
        self,
        file_bytes: bytes,
        filename: str,
        session_id: str = "default",
    ) -> ScanResult:
        """
        Run all security checks on an uploaded file.
        Returns ScanResult with safe=True/False, warnings, and errors.
        """
        result = ScanResult(safe=True)
        result.file_hash = hashlib.sha256(file_bytes).hexdigest()[:16]

        # 1. Rate limiting
        rate_err = self._check_rate_limit(session_id)
        if rate_err:
            result.safe = False
            result.errors.append(rate_err)
            return result

        # 2. File size
        size_err = self._check_file_size(file_bytes, filename)
        if size_err:
            result.safe = False
            result.errors.append(size_err)
            return result

        # 3. File extension
        ext = Path(filename).suffix.lower()
        if ext not in MAGIC_BYTES:
            result.safe = False
            result.errors.append(
                f"File type '{ext}' is not allowed. "
                f"Supported: {', '.join(MAGIC_BYTES.keys())}"
            )
            return result

        # 4. Magic bytes validation
        magic_err = self._check_magic_bytes(file_bytes, ext)
        if magic_err:
            result.safe = False
            result.errors.append(magic_err)
            return result

        # 5. Decode content for text-based checks
        try:
            content = file_bytes.decode("utf-8", errors="replace")
        except Exception:
            content = ""

        # For binary formats (PDF, DOCX), skip text-based content checks
        if ext in (".pdf", ".docx"):
            result.cleaned_content = ""
            # Increment rate limit counter
            self._increment_rate_limit(session_id)
            return result

        # 6. Dangerous pattern scan
        danger_errs = self._scan_dangerous_patterns(content, filename)
        if danger_errs:
            result.safe = False
            result.errors.extend(danger_errs)
            return result

        # 7. Suspicious pattern scan (warnings, not blocking)
        suspicious_warnings = self._scan_suspicious_patterns(content)
        result.warnings.extend(suspicious_warnings)

        # 8. Content sanitization
        result.cleaned_content = self._sanitize_content(content)

        # 9. Content quality check
        quality_err = self._check_content_quality(result.cleaned_content)
        if quality_err:
            result.safe = False
            result.errors.append(quality_err)
            return result

        # Increment rate limit counter
        self._increment_rate_limit(session_id)

        logger.info(
            f"Security scan PASSED for '{filename}' "
            f"(hash={result.file_hash}, warnings={len(result.warnings)})"
        )
        return result

    # ── Individual Checks ─────────────────────────────────────────────

    def _check_rate_limit(self, session_id: str) -> Optional[str]:
        count = self._session_uploads.get(session_id, 0)
        if count >= self.max_uploads_per_session:
            return (
                f"Upload limit reached ({self.max_uploads_per_session} per session). "
                f"Please try again later."
            )
        return None

    def _increment_rate_limit(self, session_id: str):
        self._session_uploads[session_id] = self._session_uploads.get(session_id, 0) + 1

    def _check_file_size(self, file_bytes: bytes, filename: str) -> Optional[str]:
        size_mb = len(file_bytes) / (1024 * 1024)
        if len(file_bytes) > self.max_size_bytes:
            return f"File too large ({size_mb:.1f}MB). Maximum is {self.max_size_bytes // (1024*1024)}MB."
        if len(file_bytes) < 10:
            return "File is empty or too small."
        return None

    def _check_magic_bytes(self, file_bytes: bytes, ext: str) -> Optional[str]:
        expected = MAGIC_BYTES.get(ext)
        if expected is None:
            return None  # text files — no magic bytes to check

        for magic in expected:
            if file_bytes[:len(magic)] == magic:
                return None

        return (
            f"File content doesn't match the '{ext}' format. "
            f"The file may be corrupted or mislabeled."
        )

    def _scan_dangerous_patterns(self, content: str, filename: str) -> list[str]:
        errors = []
        for i, regex in enumerate(DANGEROUS_REGEX):
            match = regex.search(content)
            if match:
                pattern_desc = DANGEROUS_PATTERNS[i][:40]
                errors.append(
                    f"Security risk detected: potentially dangerous content "
                    f"(pattern: {pattern_desc}). Upload rejected."
                )
                logger.warning(
                    f"DANGEROUS pattern found in '{filename}': "
                    f"{pattern_desc} at position {match.start()}"
                )
                break  # One is enough to reject
        return errors

    def _scan_suspicious_patterns(self, content: str) -> list[str]:
        warnings = []
        for regex in SUSPICIOUS_REGEX:
            if regex.search(content):
                warnings.append(
                    "Document may contain sensitive information "
                    "(passwords, keys, or personal data). "
                    "Please ensure no secrets are included."
                )
                break  # One warning is enough
        return warnings

    def _sanitize_content(self, content: str) -> str:
        """Remove potentially dangerous HTML/script content while preserving text."""
        # Strip HTML tags
        cleaned = re.sub(r"<[^>]+>", " ", content)
        # Normalize whitespace
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        # But preserve paragraph breaks for chunking
        cleaned = content  # Actually keep original for chunking
        # Just strip obvious HTML tags
        cleaned = re.sub(r"<script[^>]*>.*?</script>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<style[^>]*>.*?</style>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<iframe[^>]*>.*?</iframe>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<object[^>]*>.*?</object>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r"<embed[^>]*>", "", cleaned, flags=re.IGNORECASE)
        return cleaned

    def _check_content_quality(self, content: str) -> Optional[str]:
        """Ensure content has minimum quality for the knowledge base."""
        if len(content.strip()) < 100:
            return (
                "Document is too short (minimum 100 characters of readable content). "
                "Please upload a more substantial document."
            )

        # Check if content is mostly gibberish (very low word diversity)
        words = re.findall(r"[a-zA-Z]{3,}", content[:2000])
        if len(words) < 10:
            return (
                "Document doesn't contain enough readable text. "
                "Please upload a document with Pega-related content."
            )

        # Check for excessive repetition
        if words:
            unique_ratio = len(set(w.lower() for w in words)) / len(words)
            if unique_ratio < 0.1:
                return (
                    "Document appears to contain repetitive or low-quality content. "
                    "Please upload meaningful Pega documentation."
                )

        return None


# Singleton scanner instance
_scanner = None

def get_scanner() -> UploadScanner:
    global _scanner
    if _scanner is None:
        _scanner = UploadScanner()
    return _scanner
