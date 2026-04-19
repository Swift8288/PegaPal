#!/usr/bin/env python3
"""
Quick rebuild — deletes old ChromaDB, rebuilds index with all docs including RPA.
Run: python quick_rebuild.py
Then: streamlit run ui/app.py
"""
import shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import CHROMA_DIR, IDF_FILE

# Step 1: Delete old data
if CHROMA_DIR.exists():
    shutil.rmtree(CHROMA_DIR)
    print(f"✓ Deleted old ChromaDB at {CHROMA_DIR}")

if IDF_FILE.exists():
    IDF_FILE.unlink()
    print(f"✓ Deleted old IDF file")

# Step 2: Rebuild
from indexer.index_docs import PegaIndexer

indexer = PegaIndexer()
total = indexer.index_directory()
print(f"\n✅ Done! {total} chunks indexed (was 847, now includes RPA docs)")
print(f"Stats: {indexer.stats()}")
print("\nRestart Streamlit: streamlit run ui/app.py")
