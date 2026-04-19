# 🔧🤖 PegaPal — AI-Powered Pega Assistant

A free, community-driven RAG-powered assistant for Pega developers.
Debug errors, learn concepts, compare approaches — powered by 230+ expert documents and Claude AI.

**Live Demo:** [pegapal.streamlit.app](https://pegapal.streamlit.app) *(update after deployment)*

## Features

- **Debug Errors** — Paste any PEGA alert code, Java exception, or stack trace and get root causes + fixes
- **Learn Concepts** — Ask about Data Pages, Activities, Case Management, RPA, and more
- **230+ Knowledge Base** — Curated docs covering all major Pega topics with source citations
- **Community Contributions** — Upload your own docs to grow the knowledge base
- **Multi-LLM Support** — Claude, Groq (free), Gemini (free), OpenAI with auto-fallback
- **AI-Powered RAG** — Every answer is grounded in the KB with confidence levels and match %
- **Admin Panel** — Review, approve/reject community uploads with security scanning
- **Interactive Tour** — Built-in product tour for new users

## Quick Start (Local)

```bash
# 1. Clone and install
git clone https://github.com/yourusername/PegaPal.git
cd PegaPal
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env — add at least one API key (Groq is free: console.groq.com)

# 3. Build the knowledge base index
python quick_rebuild.py

# 4. Launch
streamlit run ui/app.py
```

Open [localhost:8501](http://localhost:8501) and start asking!

## Deploy to Streamlit Cloud (Free)

1. **Push to GitHub** (see steps below)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"** → select your repo → set main file: `ui/app.py`
4. Go to **Settings → Secrets** and paste your secrets:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   LLM_BACKEND = "claude"
   EMBEDDING_BACKEND = "tfidf"
   ADMIN_PASSWORD = "your_secure_password"
   ```
5. Click **Deploy** — your app will be live at `yourapp.streamlit.app`

### Push to GitHub (First Time)

```bash
cd PegaPal
git init
git add .
git commit -m "Initial commit — PegaPal v1.0"
git remote add origin https://github.com/yourusername/PegaPal.git
git branch -M main
git push -u origin main
```

## Tech Stack

| Component | Tool | Cost |
|-----------|------|------|
| LLM (primary) | Claude Sonnet (Anthropic) | BYOK |
| LLM (free) | Groq — Llama 3.3 70B | Free |
| LLM (free) | Google Gemini 2.0 Flash | Free |
| Embeddings | TF-IDF (pure Python) | Free |
| Vector DB | ChromaDB (persistent) | Free |
| Frontend | Streamlit | Free |
| Hosting | Streamlit Community Cloud | Free |

## Project Structure

```
PegaPal/
├── config.py              # Central configuration + system prompt
├── ui/
│   └── app.py             # Streamlit chat UI (main entry point)
├── rag/
│   └── query.py           # RAG engine — retrieval + LLM generation
├── indexer/
│   ├── index_docs.py      # Chunk + embed + store in ChromaDB
│   ├── community.py       # Community upload processor
│   └── security.py        # Upload security scanner
├── crawler/
│   └── seed_kb_*.py       # Knowledge base seed scripts
├── data/
│   ├── chroma_db/         # Persisted vector store
│   ├── raw_docs/          # Curated knowledge base documents
│   └── community_docs/    # Community-uploaded documents
├── .streamlit/
│   └── config.toml        # Streamlit theme + settings
├── requirements.txt
├── quick_rebuild.py        # One-command KB rebuild
├── .env.example
└── README.md
```

## Configuration

All settings in `config.py`, override via `.env` or Streamlit secrets:

| Setting | Options | Default |
|---------|---------|---------|
| `LLM_BACKEND` | `claude`, `groq`, `gemini`, `openai` | `groq` |
| `EMBEDDING_BACKEND` | `tfidf`, `sbert`, `ollama` | `tfidf` |
| `TOP_K` | 1-20 | 8 |
| `CHUNK_SIZE` | 400-1200 | 800 |
| `ADMIN_PASSWORD` | any string | `pegapal_admin_2024` |

## Contributing

1. Fork the repo
2. Upload docs via the sidebar or add JSON files to `data/raw_docs/`
3. Run `python quick_rebuild.py` to rebuild the index
4. Submit a PR

## License

MIT — free to use, modify, and distribute.

Built by **Santosh Thammali** — a Pega developer, for Pega developers.
