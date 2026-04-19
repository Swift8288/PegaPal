"""
Quick test: runs the full pipeline end-to-end.
Usage: python test_pipeline.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

print("=" * 60)
print("PEGA DEBUG ASSISTANT — END-TO-END TEST")
print("=" * 60)

# Step 1: Test config loads
print("\n[1/4] Loading config...")
try:
    from config import GROQ_API_KEY, EMBEDDING_BACKEND, LLM_BACKEND
    print(f"  EMBEDDING_BACKEND = {EMBEDDING_BACKEND}")
    print(f"  LLM_BACKEND = {LLM_BACKEND}")
    print(f"  GROQ_API_KEY = {'SET (' + GROQ_API_KEY[:8] + '...)' if GROQ_API_KEY else 'NOT SET!'}")
    if not GROQ_API_KEY:
        print("  ERROR: Set GROQ_API_KEY in .env file!")
        sys.exit(1)
    print("  OK")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

# Step 2: Test indexer / search
print("\n[2/4] Testing search...")
try:
    from indexer.index_docs import PegaIndexer
    indexer = PegaIndexer()
    stats = indexer.stats()
    print(f"  Collection: {stats['collection']}, Chunks: {stats['total_chunks']}")
    if stats['total_chunks'] == 0:
        print("  ERROR: No chunks indexed! Run: python -m crawler.seed_kb && python -m indexer.index_docs")
        sys.exit(1)
    hits = indexer.search("Obj-Save lock error", top_k=3)
    for h in hits:
        title = h['metadata'].get('title', 'Unknown')
        dist = round(h['distance'], 4)
        print(f"  Hit: {title} (distance={dist})")
    print("  OK")
except Exception as e:
    print(f"  FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

# Step 3: Test Groq API (raw HTTP — bypasses SDK issues)
print("\n[3/4] Testing Groq API (raw HTTP)...")
try:
    import requests
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'hello' in one word."},
            ],
            "temperature": 0.1,
            "max_tokens": 10,
        },
        timeout=30,
    )
    if resp.status_code == 200:
        answer = resp.json()["choices"][0]["message"]["content"]
        print(f"  Groq response: {answer}")
        print("  OK")
    else:
        print(f"  FAILED: HTTP {resp.status_code}")
        print(f"  Response: {resp.text[:200]}")
        sys.exit(1)
except Exception as e:
    print(f"  FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

# Step 4: Test full RAG pipeline
print("\n[4/4] Testing full RAG pipeline...")
try:
    from rag.query import PegaDebugEngine
    engine = PegaDebugEngine()
    result = engine.query("Obj-Save lock error in Queue Processor")
    print(f"  Confidence: {result.confidence}")
    print(f"  LLM Backend: {result.llm_backend}")
    print(f"  Sources: {len(result.sources)}")
    print(f"  Answer preview: {result.answer[:150]}...")
    print("  OK")
except Exception as e:
    print(f"  FAILED: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED! Your Pega Debug Assistant is working.")
print("Run: streamlit run ui/app.py")
print("=" * 60)
