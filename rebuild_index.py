#!/usr/bin/env python3
"""
PegaPal — Rebuild Search Index

Run this script after changing the embedding algorithm to rebuild
the ChromaDB index with new embeddings and IDF weights.

Usage:
    python rebuild_index.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from indexer.index_docs import PegaIndexer

if __name__ == "__main__":
    print("🔄 Rebuilding PegaPal search index...")
    print("   This will delete the old index and re-embed all documents.")
    print()

    indexer = PegaIndexer()
    total = indexer.rebuild_index()

    print(f"\n✅ Rebuild complete!")
    print(f"   Total chunks indexed: {total}")
    print(f"   Stats: {indexer.stats()}")
    print()
    print("You can now restart Streamlit: streamlit run ui/app.py")
