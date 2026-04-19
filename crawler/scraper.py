"""
Pega Documentation Crawler
Scrapes docs.pega.com and support.pega.com for debugging-related pages.
Saves raw HTML/text to data/raw_docs/ for later indexing.
"""

import hashlib
import json
import logging
import re
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import (
    CRAWL_DELAY,
    MAX_PAGES,
    PEGA_SESSION_COOKIE,
    RAW_DOCS_DIR,
    USER_AGENT,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ── Seed URLs ──────────────────────────────────────────────────────────
SEED_URLS = [
    # ── Phase 1: Method References (Obj-*) ──
    "https://docs.pega.com/bundle/platform/page/platform/pxref/objsave-method.html",
    "https://docs.pega.com/bundle/platform/page/platform/pxref/objopen-method.html",
    "https://docs.pega.com/bundle/platform/page/platform/pxref/objdelete-method.html",
    "https://docs.pega.com/bundle/platform/page/platform/pxref/objlist-method.html",
    "https://docs.pega.com/bundle/platform/page/platform/pxref/objbrowse-method.html",
    "https://docs.pega.com/bundle/platform/page/platform/pxref/objrefresh-method.html",
    "https://docs.pega.com/bundle/platform/page/platform/pxref/objvalidate-method.html",
    "https://docs.pega.com/bundle/platform/page/platform/pxref/activity-methods.html",

    # ── Phase 1: Tracer / Debugging ──
    "https://docs.pega.com/bundle/platform/page/platform/tracer/tracer-overview.html",
    "https://docs.pega.com/bundle/platform/page/platform/tracer/using-tracer.html",
    "https://docs.pega.com/bundle/platform/page/platform/tracer/tracer-settings.html",

    # ── Phase 1: Guardrails ──
    "https://docs.pega.com/bundle/platform/page/platform/guardrails/guardrails-landing-page.html",

    # ── Phase 1: Data Integrity & Locking ──
    "https://docs.pega.com/bundle/platform/page/platform/datamanagement/data-integrity-landing.html",
    "https://docs.pega.com/bundle/platform/page/platform/datamanagement/locking-overview.html",
    "https://docs.pega.com/bundle/platform/page/platform/datamanagement/optimistic-locking.html",
    "https://docs.pega.com/bundle/platform/page/platform/datamanagement/pessimistic-locking.html",
    "https://docs.pega.com/bundle/platform/page/platform/datamanagement/commit-and-rollback.html",

    # ── Phase 2: Queue Processors ──
    "https://docs.pega.com/bundle/platform/page/platform/queueprocessor/queue-processor-landing-page.html",
    "https://docs.pega.com/bundle/platform/page/platform/queueprocessor/creating-queue-processor.html",
    "https://docs.pega.com/bundle/platform/page/platform/queueprocessor/debugging-queue-processors.html",
    "https://docs.pega.com/bundle/platform/page/platform/queueprocessor/queue-processor-error-handling.html",

    # ── Phase 2: Job Scheduler / Agents ──
    "https://docs.pega.com/bundle/platform/page/platform/jobscheduler/job-scheduler-landing-page.html",
    "https://docs.pega.com/bundle/platform/page/platform/agents/agent-schedule-landing.html",
    "https://docs.pega.com/bundle/platform/page/platform/agents/debugging-agents.html",

    # ── Phase 2: Exception Handling ──
    "https://docs.pega.com/bundle/platform/page/platform/flowprocessing/exception-handling-overview.html",
    "https://docs.pega.com/bundle/platform/page/platform/flowprocessing/flow-action-processing.html",

    # ── Phase 3: Connectors & Integrations ──
    "https://docs.pega.com/bundle/platform/page/platform/connectors/connector-and-metadata-landing-page.html",
    "https://docs.pega.com/bundle/platform/page/platform/connectors/rest-connector.html",
    "https://docs.pega.com/bundle/platform/page/platform/connectors/soap-connector.html",
    "https://docs.pega.com/bundle/platform/page/platform/connectors/connect-rest-errors.html",
    "https://docs.pega.com/bundle/platform/page/platform/connectors/connect-soap-errors.html",

    # ── Phase 3: Declare Expressions ──
    "https://docs.pega.com/bundle/platform/page/platform/declaratives/declare-expression-overview.html",
    "https://docs.pega.com/bundle/platform/page/platform/declaratives/declare-expression-debugging.html",
    "https://docs.pega.com/bundle/platform/page/platform/declaratives/declare-trigger.html",
    "https://docs.pega.com/bundle/platform/page/platform/declaratives/declare-index.html",

    # ── Phase 3: Database Mapping & Errors ──
    "https://docs.pega.com/bundle/platform/page/platform/datamanagement/database-mapping-overview.html",
    "https://docs.pega.com/bundle/platform/page/platform/datamanagement/troubleshooting-database-issues.html",
    "https://docs.pega.com/bundle/platform/page/platform/datamanagement/class-table-mapping.html",

    # ── Phase 3: Security & Authentication ──
    "https://docs.pega.com/bundle/platform/page/platform/security/security-landing-page.html",
    "https://docs.pega.com/bundle/platform/page/platform/security/authentication-overview.html",
    "https://docs.pega.com/bundle/platform/page/platform/security/oauth2-provider.html",
    "https://docs.pega.com/bundle/platform/page/platform/security/sso-overview.html",

    # ── Phase 3: SLA & Urgency ──
    "https://docs.pega.com/bundle/platform/page/platform/sla/service-level-agreement-overview.html",
    "https://docs.pega.com/bundle/platform/page/platform/sla/urgency-calculation.html",

    # ── Phase 3: Reports & Lists ──
    "https://docs.pega.com/bundle/platform/page/platform/reporting/report-definition-overview.html",
    "https://docs.pega.com/bundle/platform/page/platform/reporting/troubleshooting-reports.html",

    # ── Phase 3: Performance & Caching ──
    "https://docs.pega.com/bundle/platform/page/platform/performance/pega-performance-overview.html",
    "https://docs.pega.com/bundle/platform/page/platform/performance/caching-overview.html",
    "https://docs.pega.com/bundle/platform/page/platform/performance/clipboard-performance.html",
]

# ── Pega Community Seed URLs ───────────────────────────────────────────
COMMUNITY_SEED_URLS = [
    # Popular debugging discussions on collaborate.pega.com
    "https://collaborate.pega.com/discussion/obj-save-locking-issues",
    "https://collaborate.pega.com/discussion/queue-processor-error-handling",
    "https://collaborate.pega.com/discussion/tracer-tips-and-tricks",
    "https://collaborate.pega.com/discussion/rest-connector-troubleshooting",
    "https://collaborate.pega.com/discussion/declare-expression-circular-reference",
    "https://collaborate.pega.com/discussion/pega-performance-tuning",
    "https://collaborate.pega.com/discussion/agent-not-running",
    "https://collaborate.pega.com/discussion/sso-authentication-errors",
]

# URL patterns we want to follow (stay within Pega docs + community)
ALLOWED_PATTERNS = [
    r"docs\.pega\.com/bundle/platform/page/platform/",
    r"docs\.pega\.com/bundle/platform/page/platform/pxref/",
    r"support\.pega\.com/support-doc/",
    r"collaborate\.pega\.com/discussion/",
    r"collaborate\.pega\.com/question/",
]


class PegaCrawler:
    """Crawls Pega documentation sites and saves content for indexing."""

    def __init__(
        self,
        output_dir: Path = RAW_DOCS_DIR,
        max_pages: int = MAX_PAGES,
        delay: float = CRAWL_DELAY,
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_pages = max_pages
        self.delay = delay
        self.visited: set[str] = set()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

        if PEGA_SESSION_COOKIE:
            self.session.cookies.set("PegaSessionCookie", PEGA_SESSION_COOKIE)

    def _url_hash(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()[:12]

    def _is_allowed(self, url: str) -> bool:
        return any(re.search(p, url) for p in ALLOWED_PATTERNS)

    def _extract_content(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract meaningful text content from a Pega doc page."""
        # Remove nav, footer, sidebar noise
        for tag in soup.find_all(["nav", "footer", "script", "style", "aside"]):
            tag.decompose()

        # Try to find the main content area
        main = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", class_=re.compile(r"content|body|main", re.I))
            or soup.find("div", id=re.compile(r"content|body|main", re.I))
        )
        container = main if main else soup.body if soup.body else soup

        title = ""
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)

        # Extract text, preserving some structure
        paragraphs = []
        for element in container.find_all(["h1", "h2", "h3", "h4", "p", "li", "td", "pre", "code"]):
            text = element.get_text(separator=" ", strip=True)
            if text and len(text) > 10:
                prefix = ""
                if element.name in ("h1", "h2", "h3", "h4"):
                    prefix = f"{'#' * int(element.name[1])} "
                paragraphs.append(f"{prefix}{text}")

        content = "\n\n".join(paragraphs)

        return {
            "url": url,
            "title": title,
            "content": content,
            "content_length": len(content),
        }

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        """Extract and filter links from a page."""
        links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            full_url = urljoin(base_url, href)
            # Remove fragments
            full_url = full_url.split("#")[0]
            if full_url not in self.visited and self._is_allowed(full_url):
                links.append(full_url)
        return list(set(links))

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a single page with error handling."""
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return None

    def save_doc(self, doc: dict) -> Path:
        """Save extracted doc to JSON file."""
        filename = f"{self._url_hash(doc['url'])}.json"
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)
        return filepath

    def _extract_community_content(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract content from collaborate.pega.com discussion/question pages."""
        for tag in soup.find_all(["nav", "footer", "script", "style", "aside"]):
            tag.decompose()

        title = ""
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)

        # Community pages: grab the question/discussion + all answers/replies
        paragraphs = []

        # Main post
        main_post = (
            soup.find("div", class_=re.compile(r"question-body|discussion-body|post-body", re.I))
            or soup.find("article")
            or soup.find("div", class_=re.compile(r"content", re.I))
        )
        if main_post:
            text = main_post.get_text(separator=" ", strip=True)
            if text:
                paragraphs.append(f"## Question/Discussion\n{text}")

        # Replies / answers
        replies = soup.find_all("div", class_=re.compile(r"reply|answer|comment|response", re.I))
        for i, reply in enumerate(replies, 1):
            text = reply.get_text(separator=" ", strip=True)
            if text and len(text) > 20:
                paragraphs.append(f"## Reply {i}\n{text}")

        # Fallback: grab all text if structured extraction failed
        if not paragraphs:
            container = soup.body if soup.body else soup
            for element in container.find_all(["h1", "h2", "h3", "p", "li", "pre", "code"]):
                text = element.get_text(separator=" ", strip=True)
                if text and len(text) > 10:
                    paragraphs.append(text)

        content = "\n\n".join(paragraphs)
        return {
            "url": url,
            "title": title,
            "content": content,
            "content_length": len(content),
            "source_type": "community",
        }

    def crawl(self, seed_urls: Optional[list[str]] = None, include_community: bool = False) -> list[dict]:
        """
        BFS crawl starting from seed URLs.
        If include_community=True, also crawls collaborate.pega.com seeds.
        Returns list of extracted documents.
        """
        queue = list(seed_urls or SEED_URLS)
        if include_community:
            queue.extend(COMMUNITY_SEED_URLS)

        documents = []

        logger.info(f"Starting crawl with {len(queue)} seed URLs (max {self.max_pages} pages)")

        while queue and len(self.visited) < self.max_pages:
            url = queue.pop(0)
            if url in self.visited:
                continue

            self.visited.add(url)
            logger.info(f"[{len(self.visited)}/{self.max_pages}] Crawling: {url}")

            soup = self.fetch_page(url)
            if not soup:
                continue

            # Use community extractor for collaborate.pega.com
            if "collaborate.pega.com" in url:
                doc = self._extract_community_content(soup, url)
            else:
                doc = self._extract_content(soup, url)

            if doc["content_length"] > 50:
                self.save_doc(doc)
                documents.append(doc)
                logger.info(f"  -> Saved: {doc['title'][:60]} ({doc['content_length']} chars)")
            else:
                logger.info(f"  x  Skipped (too short): {url}")

            new_links = self._extract_links(soup, url)
            queue.extend(new_links)

            time.sleep(self.delay)

        logger.info(f"Crawl complete. {len(documents)} documents saved to {self.output_dir}")
        return documents

    def crawl_single(self, url: str) -> Optional[dict]:
        """Crawl a single URL (for adding individual docs later)."""
        soup = self.fetch_page(url)
        if not soup:
            return None

        if "collaborate.pega.com" in url:
            doc = self._extract_community_content(soup, url)
        else:
            doc = self._extract_content(soup, url)

        if doc["content_length"] > 50:
            self.save_doc(doc)
            return doc
        return None


def add_url(url: str) -> Optional[dict]:
    """Convenience function: crawl + save a single URL."""
    crawler = PegaCrawler()
    return crawler.crawl_single(url)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pega Documentation Crawler")
    parser.add_argument("--community", action="store_true", help="Also crawl collaborate.pega.com")
    parser.add_argument("--max-pages", type=int, default=MAX_PAGES, help=f"Max pages to crawl (default: {MAX_PAGES})")
    args = parser.parse_args()

    crawler = PegaCrawler(max_pages=args.max_pages)
    docs = crawler.crawl(include_community=args.community)
    print(f"\nDone! Crawled {len(docs)} documents.")
