"""
PegaPal — Daily Knowledge Base Refresh Script
Re-indexes all community-uploaded documents and core KB.
Run manually:  python scripts/refresh_kb.py
Schedule via:  cron (Linux) or Task Scheduler (Windows)

Cron example (daily at 2 AM):
    0 2 * * * cd /path/to/PegaPal && python scripts/refresh_kb.py >> logs/refresh.log 2>&1

What it does:
1. Re-indexes all community docs (picks up any embedding backend changes)
2. Re-indexes core KB docs (optional, with --full flag)
3. Logs stats and timing
"""

import argparse
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import RAW_DOCS_DIR
from indexer.index_docs import PegaIndexer
from indexer.community import CommunityIndexer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def refresh(full: bool = False):
    """Run the KB refresh."""
    start = time.time()
    logger.info("=" * 60)
    logger.info("PegaPal — Knowledge Base Refresh Starting")
    logger.info("=" * 60)

    # Initialize indexer
    indexer = PegaIndexer()
    logger.info(f"Current KB stats: {indexer.stats()}")

    # Step 1: Refresh community docs
    logger.info("\n--- Community Documents ---")
    ci = CommunityIndexer(indexer=indexer)
    community_stats = ci.get_stats()
    logger.info(f"Community docs tracked: {community_stats['total_docs']}")

    result = ci.refresh_all()
    logger.info(f"Community refresh: {result['refreshed']} docs, {result['chunks']} chunks re-indexed")

    # Step 2: Optionally re-index core KB
    if full:
        logger.info("\n--- Core Knowledge Base (full re-index) ---")
        total = indexer.index_directory(RAW_DOCS_DIR)
        logger.info(f"Core KB: {total} chunks re-indexed")

    # Done
    elapsed = time.time() - start
    logger.info(f"\n{'=' * 60}")
    logger.info(f"Refresh complete in {elapsed:.1f}s")
    logger.info(f"Final KB stats: {indexer.stats()}")
    logger.info(f"{'=' * 60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PegaPal KB Refresh")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Also re-index core KB documents (not just community)",
    )
    args = parser.parse_args()
    refresh(full=args.full)
