"""
PegaPal — Your AI-Powered Pega Companion
Streamlit Chat UI (v4 — Community Uploads)
Run: streamlit run ui/app.py
"""

# ── SQLite fix for Streamlit Cloud (must run before any chromadb import) ──
try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

# ── Page Config (MUST be first Streamlit command) ─────────────────────
st.set_page_config(
    page_title="PegaPal — AI Pega Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

from config import (
    ANTHROPIC_API_KEY,
    GROQ_API_KEY,
    LLM_BACKEND,
    MAX_UPLOAD_SIZE_MB,
)

# ── Inline SVG Logo (dual chat-bubble bot) ───────────────────────────
LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="{size}" height="{size}">
  <!-- Orange chat bubble (behind, left) -->
  <rect x="15" y="45" width="95" height="82" rx="16" fill="#f97316" />
  <polygon points="35,127 50,127 28,148" fill="#f97316" />
  <!-- Face on orange bubble -->
  <circle cx="48" cy="78" r="6" fill="#fff" opacity="0.9" />
  <circle cx="72" cy="78" r="6" fill="#fff" opacity="0.9" />
  <rect x="52" y="96" width="18" height="4" rx="2" fill="#fff" opacity="0.9" />
  <!-- Blue chat bubble (front, right) -->
  <rect x="80" y="28" width="105" height="92" rx="18" fill="#4f46e5" />
  <polygon points="148,120 162,120 170,142" fill="#4f46e5" />
  <!-- Antenna -->
  <line x1="132" y1="28" x2="132" y2="10" stroke="#f97316" stroke-width="4" stroke-linecap="round" />
  <circle cx="132" cy="6" r="6" fill="#f97316" />
  <!-- Eyes on blue bubble -->
  <rect x="105" y="54" width="20" height="20" rx="4" fill="#fff" />
  <rect x="135" y="54" width="20" height="20" rx="4" fill="#fff" />
  <rect x="110" y="59" width="10" height="10" rx="2" fill="#1e293b" />
  <rect x="140" y="59" width="10" height="10" rx="2" fill="#1e293b" />
  <!-- Mouth on blue bubble -->
  <rect x="116" y="86" width="28" height="5" rx="2.5" fill="#fff" opacity="0.9" />
</svg>"""

def logo(size=40, uid="main"):
    """Render inline logo. uid is unused now but kept for API compat."""
    return LOGO_SVG.format(size=size, uid=uid)


# ── Custom CSS (ADA-compliant, light-theme friendly) ─────────────────
st.markdown("""
<style>
    /* ── Reduce Streamlit default top padding ── */
    .block-container { padding-top: 1rem !important; }

    /* ── Main header (compact dark banner) ── */
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #0f172a 100%);
        padding: 0.7rem 1.5rem; border-radius: 10px; margin-bottom: 0.5rem;
        border-left: 4px solid #f97316;
        display: flex; align-items: center; gap: 0.8rem;
    }
    .main-header .logo-wrap { flex-shrink: 0; }
    .main-header .text-wrap h1 { color: #ffffff; font-size: 1.3rem; margin: 0; font-weight: 700; }
    .main-header .text-wrap .brand-accent { color: #f97316; }
    .main-header .text-wrap p { color: #cbd5e1; font-size: 0.8rem; margin: 0.1rem 0 0 0; }

    /* ── Sidebar brand — dark text on light bg ── */
    .sidebar-brand { display: flex; align-items: center; gap: 0.7rem; padding: 0.3rem 0; }
    .sidebar-brand h2 { color: #1e293b; margin: 0; font-size: 1.3rem; font-weight: 700; }
    .sidebar-brand .accent { color: #ea580c; }

    /* ── Hero section (enhanced) ── */
    .hero { text-align: center; padding: 1.5rem 1rem 1.2rem 1rem; }
    .hero-logo { margin-bottom: 0.5rem; }
    .hero h2 { color: #ea580c; font-size: 1.8rem; margin-bottom: 0.3rem; font-weight: 700; }
    .hero p { color: #475569; font-size: 0.95rem; max-width: 600px; margin: 0 auto; line-height: 1.6; }
    .hero strong { color: #334155; }

    /* ── Feature pills ── */
    .feature-pills { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin: 1.2rem 0 0.5rem; }
    .fpill {
        padding: 5px 14px; border-radius: 20px; font-size: 0.78rem; font-weight: 600;
        display: inline-block;
    }
    .fpill-red    { background: #fef2f2; color: #ef4444; border: 1px solid #fecaca; }
    .fpill-amber  { background: #fffbeb; color: #d97706; border: 1px solid #fde68a; }
    .fpill-blue   { background: #eff6ff; color: #3b82f6; border: 1px solid #bfdbfe; }
    .fpill-green  { background: #ecfdf5; color: #10b981; border: 1px solid #a7f3d0; }
    .fpill-purple { background: #f5f3ff; color: #8b5cf6; border: 1px solid #ddd6fe; }

    /* ── Feature cards (dark bg — light text OK) ── */
    .feature-card { background: linear-gradient(135deg, #1e293b, #334155); border-radius: 12px; padding: 1.5rem; min-height: 180px; }
    .feature-card h4 { margin-top: 0; font-size: 1rem; }
    .feature-card p { color: #e2e8f0; font-size: 0.88rem; line-height: 1.5; }
    .card-green  { border-top: 3px solid #22c55e; }
    .card-green h4  { color: #4ade80; }
    .card-blue   { border-top: 3px solid #3b82f6; }
    .card-blue h4   { color: #60a5fa; }
    .card-orange { border-top: 3px solid #f97316; }
    .card-orange h4 { color: #fb923c; }
    .card-purple { border-top: 3px solid #a855f7; }
    .card-purple h4 { color: #c084fc; }

    /* ── Tour step card ── */
    .tour-card {
        border-radius: 16px; padding: 2rem; max-width: 640px; margin: 0 auto;
        border: 2px solid transparent;
    }
    .tour-card .tour-icon { text-align: center; font-size: 3rem; margin-bottom: 0.5rem; }
    .tour-card h3 { text-align: center; font-size: 1.4rem; color: #1e293b; margin-bottom: 0.2rem; }
    .tour-card .tour-subtitle { text-align: center; font-weight: 600; font-size: 0.85rem; margin-bottom: 1rem; }
    .tour-card .tour-desc { color: #475569; line-height: 1.7; font-size: 0.93rem; margin-bottom: 1.2rem; }
    .tour-tips {
        background: #ffffff; border-radius: 12px; padding: 1rem 1.2rem;
        border: 1px solid #e2e8f0;
    }
    .tour-tips .tips-title {
        font-weight: 700; color: #334155; margin-bottom: 0.5rem;
        font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px;
    }
    .tour-tips .tip-row { display: flex; align-items: flex-start; gap: 8px; margin-bottom: 0.3rem; }
    .tour-tips .tip-arrow { font-weight: 700; font-size: 0.85rem; }
    .tour-tips .tip-text { color: #64748b; font-size: 0.85rem; }
    .tour-counter { text-align: center; margin-top: 1rem; color: #94a3b8; font-size: 0.8rem; }

    /* ── Tour progress dots ── */
    .tour-progress { display: flex; gap: 4px; max-width: 640px; margin: 0 auto 1.2rem; }
    .tour-dot { flex: 1; height: 4px; border-radius: 2px; }

    /* ── Confidence badges — WCAG AA on white ── */
    .confidence-high    { color: #15803d; font-weight: bold; font-size: 1.05em; }
    .confidence-medium  { color: #a16207; font-weight: bold; font-size: 1.05em; }
    .confidence-low     { color: #dc2626; font-weight: bold; font-size: 1.05em; }
    .confidence-general { color: #2563eb; font-weight: bold; font-size: 1.05em; }

    /* ── Source links ── */
    .source-link { font-size: 0.8em; color: #6b7280; }

    /* ── Stats cards (dark bg — light text OK) ── */
    .stats-card {
        background: linear-gradient(135deg, #1e293b, #334155);
        border-radius: 10px; padding: 0.8rem; text-align: center; border: 1px solid #475569;
    }
    .stats-card h3 { color: #fb923c; font-size: 1.6rem; margin: 0; font-weight: 800; }
    .stats-card p  { color: #e2e8f0; font-size: 0.75rem; margin: 0.2rem 0 0 0; }

    /* Community stats — purple accent */
    .stats-card-purple h3 { color: #c084fc; }

    /* ── Chat messages ── */
    .stChatMessage { max-width: 100%; }

    /* ── Sidebar — light theme, no forced dark bg ── */
    div[data-testid="stSidebar"] .stMarkdown h1,
    div[data-testid="stSidebar"] .stMarkdown h2,
    div[data-testid="stSidebar"] .stMarkdown h3 { color: #1e293b; }
    div[data-testid="stSidebar"] .stMarkdown p,
    div[data-testid="stSidebar"] .stMarkdown span,
    div[data-testid="stSidebar"] .stMarkdown label { color: #334155; }

    /* ── Footer ── */
    .footer {
        text-align: center; padding: 1rem; color: #475569;
        font-size: 0.8rem; border-top: 1px solid #e2e8f0; margin-top: 2rem;
    }
    .footer a { color: #ea580c; text-decoration: none; font-weight: 600; }

    /* ── Tip boxes — high contrast on light bg ── */
    .tip-box {
        background: #fff7ed; border: 1px solid #fed7aa;
        border-radius: 8px; padding: 0.8rem;
        font-size: 0.85rem; color: #1e293b; margin-bottom: 0.5rem;
    }
    .tip-box strong { color: #c2410c; font-weight: 700; }

    /* ── Upload success box ── */
    .upload-success {
        background: #f0fdf4; border: 1px solid #bbf7d0;
        border-radius: 8px; padding: 0.8rem;
        font-size: 0.85rem; color: #14532d; margin-bottom: 0.5rem;
    }
    .upload-success strong { color: #15803d; font-weight: 700; }

    /* ── Recent upload entry ── */
    .upload-entry {
        background: #faf5ff; border-left: 3px solid #a855f7;
        border-radius: 0 6px 6px 0; padding: 0.5rem 0.7rem; margin-bottom: 0.4rem;
        font-size: 0.82rem; color: #1e293b;
    }
    .upload-entry strong { color: #1e293b; font-weight: 600; }
    .upload-entry .meta { color: #6b7280; font-size: 0.75rem; }

    /* ── Upload pending box ── */
    .upload-pending {
        background: #fffbeb; border: 1px solid #fde68a;
        border-radius: 8px; padding: 0.8rem;
        font-size: 0.85rem; color: #78350f; margin-bottom: 0.5rem;
    }
    .upload-pending strong { color: #92400e; font-weight: 700; }

    /* ── Upload rejected box ── */
    .upload-rejected {
        background: #fef2f2; border: 1px solid #fecaca;
        border-radius: 8px; padding: 0.8rem;
        font-size: 0.85rem; color: #7f1d1d; margin-bottom: 0.5rem;
    }
    .upload-rejected strong { color: #991b1b; font-weight: 700; }

    /* ── Admin panel ── */
    .admin-pending-card {
        background: #fffbeb; border: 1px solid #fde68a;
        border-radius: 8px; padding: 0.8rem; margin-bottom: 0.6rem;
        font-size: 0.84rem; color: #1e293b;
    }
    .admin-pending-card strong { color: #92400e; font-weight: 700; }
    .admin-pending-card .preview {
        background: #f8fafc; border-radius: 6px; padding: 0.5rem;
        font-size: 0.78rem; color: #334155; margin-top: 0.4rem;
        max-height: 120px; overflow-y: auto; white-space: pre-wrap;
    }
    .admin-badge {
        display: inline-block; background: #fef3c7; color: #92400e;
        font-size: 0.7rem; font-weight: 700; padding: 0.1rem 0.5rem;
        border-radius: 10px; margin-left: 0.3rem;
    }

    /* ── Chat input styling ── */
    div[data-testid="stChatInput"] {
        max-width: 100% !important;
    }
    div[data-testid="stChatInput"] textarea {
        font-size: 1rem !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #64748b !important;
    }
    /* ── Hide Streamlit toolbar (Deploy + dev menu) — shown only for admins ── */
    .stDeployButton,
    .stAppDeployButton,
    header[data-testid="stHeader"] .stDeployButton,
    [data-testid="stMainMenu"],
    [data-testid="stToolbar"] button[kind="header"] {
        display: none !important;
    }
    /* ── Keep sidebar toggle visible ── */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    /* ── Prevent Streamlit re-render visual artifacts ── */
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "engine" not in st.session_state:
    st.session_state.engine = None
if "engine_error" not in st.session_state:
    st.session_state.engine_error = None
if "query_count" not in st.session_state:
    st.session_state.query_count = 0
if "community_indexer" not in st.session_state:
    st.session_state.community_indexer = None
if "upload_result" not in st.session_state:
    st.session_state.upload_result = None
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False
if "processing" not in st.session_state:
    st.session_state.processing = False
if "tour_active" not in st.session_state:
    st.session_state.tour_active = False
if "tour_step" not in st.session_state:
    st.session_state.tour_step = 0


# ── Initialize Engine (lazy) ─────────────────────────────────────────
def get_engine():
    """Lazy-load the RAG engine."""
    if st.session_state.engine is None and st.session_state.engine_error is None:
        try:
            from rag.query import PegaDebugEngine
            st.session_state.engine = PegaDebugEngine()
        except Exception as e:
            st.session_state.engine_error = str(e)
    return st.session_state.engine


def get_kb_doc_count():
    """Get the number of documents in the knowledge base (raw docs + community)."""
    try:
        import json as _json
        from config import RAW_DOCS_DIR, COMMUNITY_DOCS_DIR
        count = 0
        for jf in RAW_DOCS_DIR.glob("*.json"):
            try:
                with open(jf, "r", encoding="utf-8") as f:
                    data = _json.load(f)
                count += len(data) if isinstance(data, list) else 1
            except Exception:
                count += 1
        if COMMUNITY_DOCS_DIR.exists():
            count += len(list(COMMUNITY_DOCS_DIR.glob("*.json")))
        return count
    except Exception:
        return 145  # fallback


def get_community_indexer():
    """Lazy-load the community indexer."""
    if st.session_state.community_indexer is None:
        try:
            engine = get_engine()
            if engine:
                from indexer.community import CommunityIndexer
                st.session_state.community_indexer = CommunityIndexer(indexer=engine.indexer)
        except Exception as e:
            st.error(f"Community indexer error: {e}")
    return st.session_state.community_indexer


# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""<div class="sidebar-brand">
        <div>{logo(36, "sb")}</div>
        <h2>Pega<span class="accent">Pal</span></h2>
    </div>""", unsafe_allow_html=True)
    st.caption("Your free, AI-powered Pega companion")

    # Home button — always visible
    if st.button("🏠 Home", use_container_width=True, key="sidebar_home"):
        st.session_state.messages = []
        st.session_state.tour_active = False
        st.session_state.tour_step = 0
        st.rerun()

    st.divider()

    # ── LLM Engine ────────────────────────────────────────────────────
    st.markdown("### ⚡ LLM Engine")
    llm_choice = "claude"
    st.caption("Model: **Claude Sonnet** (via Anthropic)")
    st.caption("🔮 Premium AI — fast, accurate answers")

    st.divider()

    # ── Community Upload Section ──────────────────────────────────────
    st.markdown("### 🌍 Contribute Knowledge")
    st.caption("Upload your Pega docs to help the community!")

    contributor_name = st.text_input(
        "Your name (optional)",
        placeholder="e.g. Santosh",
        key="contributor_name",
    )

    uploaded_file = st.file_uploader(
        "Upload a document",
        type=["txt", "md", "pdf", "docx", "json"],
        help=f"Max {MAX_UPLOAD_SIZE_MB}MB. Supported: TXT, MD, PDF, DOCX, JSON",
        key="community_upload",
    )

    doc_title = st.text_input(
        "Document title (optional)",
        placeholder="e.g. Queue Processor Troubleshooting Guide",
        key="doc_title",
    )

    if uploaded_file is not None:
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)

        if file_size_mb > MAX_UPLOAD_SIZE_MB:
            st.error(f"File too large ({file_size_mb:.1f}MB). Max is {MAX_UPLOAD_SIZE_MB}MB.")
        elif st.button("📤 Upload & Submit", use_container_width=True, type="primary"):
            ci = get_community_indexer()
            if ci:
                with st.spinner("Scanning and processing your document..."):
                    # Generate a unique session ID for rate limiting
                    session_id = st.session_state.get("session_id", "default")
                    if session_id == "default":
                        import uuid
                        session_id = str(uuid.uuid4())[:8]
                        st.session_state.session_id = session_id

                    result = ci.process_upload(
                        file_bytes=uploaded_file.getvalue(),
                        filename=uploaded_file.name,
                        contributor=contributor_name.strip() or "Anonymous Pega Dev",
                        title=doc_title.strip() or None,
                        session_id=session_id,
                    )
                    st.session_state.upload_result = result

                if result["success"]:
                    warn_html = ""
                    if result.get("scan_warnings"):
                        warn_html = "<br>⚠️ " + result["scan_warnings"][0]
                    st.markdown(f"""<div class="upload-pending">
                        <strong>⏳ Submitted for Review</strong><br>
                        "{result['title']}" passed security scan and is now pending admin approval.{warn_html}
                    </div>""", unsafe_allow_html=True)
                elif result.get("rejected_by") == "security_scanner":
                    st.markdown(f"""<div class="upload-rejected">
                        <strong>🛡️ Security Check Failed</strong><br>
                        {result['error']}
                    </div>""", unsafe_allow_html=True)
                else:
                    st.error(f"Upload failed: {result['error']}")
            else:
                st.warning("Send a chat message first to initialize the engine.")

    # Show recent approved community uploads
    ci = get_community_indexer()
    if ci:
        stats = ci.get_stats()
        if stats.get("pending_count", 0) > 0:
            st.caption(f"📋 {stats['pending_count']} doc(s) pending review")

        recent = ci.get_recent_uploads(5)
        if recent:
            st.markdown("")
            st.markdown("**Recent contributions:**")
            for upload in recent:
                time_str = upload["uploaded_at"][:10]
                chunks = upload.get("chunks", "?")
                st.markdown(f"""<div class="upload-entry">
                    <strong>{upload['filename']}</strong><br>
                    <span class="meta">by {upload['contributor']} · {chunks} chunks · {time_str}</span>
                </div>""", unsafe_allow_html=True)

    st.divider()

    # Product Tour — highlighted banner in sidebar
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #fff7ed, #fef3c7);
        border: 2px solid #f97316;
        border-radius: 12px;
        padding: 0.8rem 1rem;
        text-align: center;
        margin-bottom: 0.5rem;
    ">
        <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">🎯</div>
        <div style="color: #1e293b; font-weight: 700; font-size: 0.9rem;">New to PegaPal?</div>
        <div style="color: #64748b; font-size: 0.75rem; line-height: 1.4; margin-top: 0.2rem;">
            Take a quick tour to explore all features
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🎯 Take a Product Tour", use_container_width=True, type="primary"):
        st.session_state.tour_active = True
        st.session_state.tour_step = 0
        st.session_state.messages = []  # go to welcome page to show tour
        st.rerun()

    st.divider()

    # Tips
    st.markdown("### 💡 Tips")
    st.markdown("""<div class="tip-box">
        <strong>Debug errors:</strong> Paste the full error message or PEGA alert code directly in the chat.
    </div>""", unsafe_allow_html=True)
    st.markdown("""<div class="tip-box">
        <strong>Learn concepts:</strong> Ask "Explain data pages" or "Activity vs Data Transform" for clear explanations.
    </div>""", unsafe_allow_html=True)
    st.markdown("""<div class="tip-box">
        <strong>Contribute:</strong> Upload your troubleshooting notes, runbooks, or Pega guides to grow the KB!
    </div>""", unsafe_allow_html=True)

    st.divider()

    # Clear chat
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.query_count = 0
        st.rerun()

    st.divider()

    # ── Admin Panel (password-protected) ──────────────────────────────
    with st.expander("🔐 Admin Panel"):
        if not st.session_state.admin_authenticated:
            admin_pass = st.text_input(
                "Admin Password", type="password", key="admin_password",
                placeholder="Enter admin password",
            )
            if st.button("🔓 Login", key="admin_login"):
                import os
                correct_pass = os.getenv("PEGAPAL_ADMIN_PASSWORD", "") or os.getenv("ADMIN_PASSWORD", "pegapal_admin_2024")
                # Also check Streamlit secrets for cloud deployment
                if not correct_pass or correct_pass == "pegapal_admin_2024":
                    try:
                        correct_pass = st.secrets.get("ADMIN_PASSWORD", correct_pass)
                    except Exception:
                        pass
                if admin_pass == correct_pass:
                    st.session_state.admin_authenticated = True
                    st.rerun()
                else:
                    st.error("Incorrect password.")
        else:
            st.caption("✅ Authenticated as Admin")

            # Show Deploy button + dev menu only for admins
            st.markdown("""<style>
                .stDeployButton,
                .stAppDeployButton,
                header[data-testid="stHeader"] .stDeployButton,
                [data-testid="stMainMenu"],
                [data-testid="stToolbar"] button[kind="header"] {
                    display: flex !important;
                }
            </style>""", unsafe_allow_html=True)

            ci = get_community_indexer()
            if ci:
                pending = ci.get_pending_for_review()
                if pending:
                    st.markdown(f"**📋 {len(pending)} document(s) pending review:**")
                    for item in pending:
                        doc_id = item["doc_id"]
                        st.markdown(f"""<div class="admin-pending-card">
                            <strong>{item['filename']}</strong>
                            <span class="admin-badge">PENDING</span><br>
                            <span class="meta">by {item['contributor']} · {item['file_size'] / 1024:.0f}KB · {item['uploaded_at'][:10]}</span>
                            {f"<br>⚠️ {item['scan_warnings'][0]}" if item.get('scan_warnings') else ""}
                            <div class="preview">{item.get('preview', 'No preview available')}</div>
                        </div>""", unsafe_allow_html=True)

                        col_a, col_r = st.columns(2)
                        with col_a:
                            if st.button(f"✅ Approve", key=f"approve_{doc_id}", use_container_width=True):
                                with st.spinner("Indexing document..."):
                                    result = ci.approve_document(doc_id)
                                if result["success"]:
                                    st.success(f"Approved! {result['chunks']} chunks indexed.")
                                    st.rerun()
                                else:
                                    st.error(result["error"])
                        with col_r:
                            if st.button(f"❌ Reject", key=f"reject_{doc_id}", use_container_width=True):
                                result = ci.reject_document(doc_id, reason="Rejected by admin")
                                if result["success"]:
                                    st.warning(f"Rejected: {result['filename']}")
                                    st.rerun()
                                else:
                                    st.error(result["error"])
                else:
                    st.info("No pending documents to review.")

                # Show quick stats
                stats = ci.get_stats()
                st.caption(
                    f"📊 Approved: {stats['total_docs']} docs · "
                    f"Pending: {stats.get('pending_count', 0)} · "
                    f"Rejected: {stats.get('rejected_count', 0)}"
                )

            if st.button("🔒 Logout", key="admin_logout", use_container_width=True):
                st.session_state.admin_authenticated = False
                st.rerun()

    st.markdown("""<div class="footer">
        Created by <strong>Santosh Thammali</strong><br>
        Powered by <a href="https://anthropic.com">Claude</a> (Anthropic) + ChromaDB<br>
        <strong>AI-Powered Pega Assistant</strong>
    </div>""", unsafe_allow_html=True)


# ── Confidence Badge ──────────────────────────────────────────────────
def confidence_badge(level: str) -> str:
    config = {
        "HIGH": ("confidence-high", "🟢", "HIGH Confidence — answer grounded in KB"),
        "MEDIUM": ("confidence-medium", "🟡", "MEDIUM Confidence — partial match in KB"),
        "LOW": ("confidence-low", "🔴", "LOW Confidence — weak match in KB"),
        "GENERAL": ("confidence-general", "🔵", "General Knowledge — not from KB"),
    }
    css, icon, label = config.get(level, ("confidence-low", "🔴", f"{level} Confidence"))
    return f'{icon} <span class="{css}">{label}</span>'


# ── Format Response ───────────────────────────────────────────────────
def format_response(result) -> str:
    """Format a DebugResult into a readable markdown string."""
    parts = [
        confidence_badge(result.confidence),
        "",
        result.answer,
    ]

    if result.sources:
        parts.append("\n---\n**📚 Sources:**")
        for s in result.sources:
            title = s.get("title", "Unknown")
            dist = s.get("distance", 0)
            match_pct = max(0, round((1 - dist) * 100))
            # Mark community sources
            prefix = "🌍 " if "community://" in s.get("url", "") else ""
            parts.append(f"- {prefix}{title} ({match_pct}% match)")

    model_names = {
        "groq": "Llama 3.3 70B",
        "openai": "GPT-4o",
        "claude": "Claude Sonnet",
        "gemini": "Gemini 2.0 Flash",
    }
    model_label = model_names.get(result.llm_backend, result.llm_backend)
    # Show if fallback was used (backend_used differs from user's selection)
    fallback_note = ""
    if hasattr(result, '_fallback_from') and result._fallback_from:
        fallback_note = f" | 🔄 Auto-fallback from {result._fallback_from}"
    parts.append(f"\n<span class='source-link'>⚡ LLM: {result.llm_backend} | Model: {model_label}{fallback_note}</span>")
    return "\n".join(parts)


# ── Callbacks (run BEFORE render, so state is correct when page draws) ─

def _send_question(question: str):
    """Callback for quick-action buttons — updates state before render."""
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.processing = False


def _go_home():
    """Callback for Home button — clears chat before render."""
    st.session_state.messages = []
    st.session_state.query_count = 0
    st.session_state.processing = False
    # Clear any pending chat input
    if "user_chat_input" in st.session_state:
        del st.session_state["user_chat_input"]


def _on_chat_submit():
    """Callback for chat input — moves input to messages before render."""
    user_input = st.session_state.get("user_chat_input", "")
    if user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.processing = False



# (No JS injection needed — scrollable container handles layout)

# ── Main Chat Area ────────────────────────────────────────────────────

if st.session_state.messages:
    # ── CHAT MODE ─────────────────────────────────────────────────────

    # Compact header with integrated Home button
    st.markdown(f"""<div class="main-header">
        <div class="logo-wrap">{logo(36, "hdr")}</div>
        <div class="text-wrap">
            <h1>Pega<span class="brand-accent">Pal</span></h1>
            <p>debug errors · learn concepts · explore the platform</p>
        </div>
    </div>""", unsafe_allow_html=True)
    st.button("🏠 Back to Home", key="home_btn", on_click=_go_home, type="secondary")

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                st.markdown(msg["content"], unsafe_allow_html=True)
            else:
                st.markdown(msg["content"])

    # Process pending user message — TWO-PHASE approach:
    # Phase 1: produce a COMPLETE render without the LLM blocking.
    # Phase 2: on the next rerun, actually call the LLM.
    if st.session_state.messages[-1]["role"] == "user":
        if not st.session_state.processing:
            # Phase 1: just show "Processing..." and rerun immediately
            st.session_state.processing = True
            with st.chat_message("assistant"):
                st.status("🤖 PegaPal is thinking...", expanded=True).write("📡 Searching knowledge base...")
            st.rerun()
        else:
            # Phase 2: actually process
            pending_query = st.session_state.messages[-1]["content"]
            engine = get_engine()
            if engine:
                with st.chat_message("assistant"):
                    status = st.status("🤖 PegaPal is thinking...", expanded=True)
                    status.write("📡 Searching knowledge base...")
                    result = engine.query(
                        pending_query,
                        llm_backend=llm_choice,
                        chat_history=st.session_state.messages[:-1],
                    )
                    status.write("💡 Generating answer...")
                    response = format_response(result)
                    status.update(label="✅ Done!", state="complete", expanded=False)
                    st.markdown(response, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.query_count += 1
                st.session_state.processing = False
                st.rerun()  # Clean final render with response in chat history
            elif st.session_state.engine_error:
                st.session_state.processing = False
                st.error(f"Engine failed to load: {st.session_state.engine_error}")
        # During processing, stop rendering to prevent welcome page
        # buttons from lingering in the browser while LLM is working
        if st.session_state.processing:
            st.stop()

else:
    # ── WELCOME PAGE (only when chat is empty) ────────────────────

    # Tour step definitions
    TOUR_STEPS = [
        {
            "icon": "🐛", "title": "Debug Errors",
            "subtitle": "Paste any error — get root causes and fixes",
            "desc": "Paste a full PEGA alert code (like PEGA0001, PEGA0055), Java exception, or stack trace directly into the chat. PegaPal identifies the error, explains what went wrong, and gives you step-by-step fix instructions with code examples.",
            "tips": ["Paste the full error message for best results", "Include the stack trace if available", "Works with all PEGA0001–0099 alerts"],
            "color": "#ef4444", "bg": "#fef2f2",
        },
        {
            "icon": "📚", "title": "Learn Concepts",
            "subtitle": "Ask about any Pega topic — get clear explanations",
            "desc": f"Ask about Data Pages, Activities, Data Transforms, Flows, Case Management, or any Pega concept. PegaPal pulls from {get_kb_doc_count()}+ expert documents to give you accurate, detailed explanations with examples and best practices.",
            "tips": ["Try 'Explain Data Pages' or 'Activity vs Data Transform'", "Ask follow-up questions to dive deeper", "Compare concepts: 'SOAP vs REST in Pega'"],
            "color": "#f59e0b", "bg": "#fffbeb",
        },
        {
            "icon": "🔍", "title": "Search the Knowledge Base",
            "subtitle": f"{get_kb_doc_count()}+ docs on Pega topics — always up to date",
            "desc": "The knowledge base covers Case Management, RPA, DevOps, Security, Integrations (REST/SOAP/Kafka), Authentication (LDAP/SSO/OAuth), UI/Constellation, and more. Every answer includes source citations with match percentages so you know how relevant the information is.",
            "tips": ["Check the Sources section for match quality", "95%+ match = highly relevant answer", "Includes Community Wiki content"],
            "color": "#3b82f6", "bg": "#eff6ff",
        },
        {
            "icon": "📤", "title": "Upload Your Docs",
            "subtitle": "Contribute knowledge — help fellow Pega devs",
            "desc": "Upload your own troubleshooting notes, runbooks, or Pega guides through the sidebar. Supported formats: TXT, MD, PDF, DOCX, and JSON. Documents go through a security scan, then an admin reviews and approves them before they're added to the knowledge base.",
            "tips": ["Add a descriptive title for better search results", "All uploads are security-scanned automatically", "Approved docs appear with a 🌍 icon in sources"],
            "color": "#10b981", "bg": "#ecfdf5",
        },
        {
            "icon": "🛡️", "title": "Admin Panel",
            "subtitle": "Review, approve, and manage community uploads",
            "desc": "Admins can expand the Admin Panel in the sidebar to review pending uploads. Each submission shows a content preview, contributor info, and any security warnings. Approve to index into the KB, or reject to remove. Track stats on total docs, pending items, and rejections.",
            "tips": ["Review the content preview before approving", "Check security warnings on each submission", "Rejected docs are permanently deleted"],
            "color": "#8b5cf6", "bg": "#f5f3ff",
        },
        {
            "icon": "🤖", "title": "AI-Powered Answers",
            "subtitle": "Powered by Claude — fast, accurate, and sourced",
            "desc": "PegaPal uses Claude AI with Retrieval-Augmented Generation (RAG). Every answer is grounded in the knowledge base — not hallucinated. You get confidence levels (HIGH/MEDIUM), source citations, and match percentages so you can trust and verify every response.",
            "tips": ["HIGH confidence = answer from KB with strong match", "MEDIUM = partial match, verify with official docs", "Sources link back to the original documents"],
            "color": "#06b6d4", "bg": "#ecfeff",
        },
    ]

    # ── Show Tour or Welcome Page ──
    if st.session_state.tour_active:
        # ── TOUR VIEW ──
        step = TOUR_STEPS[st.session_state.tour_step]
        total = len(TOUR_STEPS)
        idx = st.session_state.tour_step

        # Progress bar (full width looks better)
        dots_html = "".join(
            f'<div class="tour-dot" style="background: {TOUR_STEPS[i]["color"] if i <= idx else "#e2e8f0"};"></div>'
            for i in range(total)
        )
        st.markdown(f'<div class="tour-progress" style="max-width: 100%;">{dots_html}</div>', unsafe_allow_html=True)

        # Step card — centered, large text
        tips_html = "".join(
            f'<div style="display: flex; align-items: flex-start; gap: 10px; margin-bottom: 8px;"><span style="color: {step["color"]}; font-weight: 700; font-size: 1.1rem;">→</span><span style="color: #475569; font-size: 1.1rem; line-height: 1.5;">{t}</span></div>'
            for t in step["tips"]
        )
        st.markdown(f"""
        <div style="
            background: {step["bg"]};
            border: 2px solid {step["color"]}30;
            border-radius: 20px;
            padding: 3rem 3.5rem;
            margin: 0.5rem auto 1.5rem;
            max-width: 800px;
        ">
            <div style="text-align: center; font-size: 4.5rem; margin-bottom: 1rem;">{step["icon"]}</div>
            <h2 style="text-align: center; color: #1e293b; font-size: 2.2rem; margin-bottom: 0.4rem; font-weight: 700;">{step["title"]}</h2>
            <p style="text-align: center; color: {step["color"]}; font-weight: 600; font-size: 1.2rem; margin-bottom: 1.5rem;">{step["subtitle"]}</p>
            <p style="color: #374151; line-height: 1.9; font-size: 1.15rem; margin-bottom: 2rem; text-align: center;">{step["desc"]}</p>
            <div style="background: #fff; border-radius: 14px; padding: 1.5rem 2rem; border: 1px solid #e2e8f0;">
                <p style="font-weight: 700; color: #1e293b; margin-bottom: 0.8rem; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.5px;">Pro Tips</p>
                {tips_html}
            </div>
            <p style="text-align: center; margin-top: 1.5rem; color: #94a3b8; font-size: 1rem;">Step {idx + 1} of {total}</p>
        </div>
        """, unsafe_allow_html=True)

        # Navigation — Previous and Next, centered
        _, nav1, nav_space, nav2, _ = st.columns([1, 1, 2, 1, 1])
        with nav1:
            if idx > 0:
                if st.button("← Previous", use_container_width=True, key="tour_prev"):
                    st.session_state.tour_step -= 1
                    st.rerun()
        with nav2:
            if idx < total - 1:
                if st.button("Next →", use_container_width=True, type="primary", key="tour_next"):
                    st.session_state.tour_step += 1
                    st.rerun()
            else:
                if st.button("✓ Start Using PegaPal", use_container_width=True, type="primary", key="tour_done"):
                    st.session_state.tour_active = False
                    st.session_state.tour_step = 0
                    st.rerun()

    else:
        # ── WELCOME PAGE (enhanced hero + feature cards + KB overview) ──

        st.markdown(f"""<div class="hero">
            <div class="hero-logo">{logo(70, "hero")}</div>
            <h2>Meet PegaPal</h2>
            <p>
                Your AI-powered companion for everything Pega.
                Debug errors, learn concepts, compare approaches, or explore any topic — powered by <strong>{get_kb_doc_count()} expert documents</strong> and growing with community contributions.
            </p>
        </div>""", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""<div class="feature-card card-green">
                <h4>🔍 Debug Errors</h4>
                <p>Paste any error — <strong>PEGA alerts</strong>,
                <strong>NullPointerException</strong>, timeouts — get root causes and fixes.</p>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("""<div class="feature-card card-blue">
                <h4>📚 Learn Concepts</h4>
                <p>Ask about <strong>Data Pages</strong>, <strong>Activities</strong>,
                design patterns — get clear explanations with examples.</p>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="feature-card card-orange">
                <h4>🏗️ Full Coverage</h4>
                <p><strong>{get_kb_doc_count()}+ docs</strong> on Case Mgmt, AI/ML, RPA, Mobile, DevOps,
                Security, Community Wiki, and all PEGA alerts.</p>
            </div>""", unsafe_allow_html=True)
        with col4:
            st.markdown("""<div class="feature-card card-purple">
                <h4>🌍 Community-Powered</h4>
                <p><strong>Upload your own docs</strong> — troubleshooting guides, runbooks,
                notes — and help fellow Pega devs!</p>
            </div>""", unsafe_allow_html=True)

        st.markdown("#### 📋 What's in the Knowledge Base")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
            **🔧 Debugging & Errors**
            - All PEGA0001–0099 alerts
            - Java exceptions guide
            - Tracer & PAL usage
            - Log file analysis
            - Security event forensics
            """)
        with col2:
            st.markdown("""
            **🏛️ Platform Features**
            - Case Management
            - Data Pages & Transforms
            - Flows & Assignments
            - UI / Constellation
            - Reporting & Dashboards
            """)
        with col3:
            st.markdown("""
            **🔌 Integrations & AI**
            - REST / SOAP / Kafka / JMS
            - SAP & Salesforce
            - Prediction Studio & NBA
            - GenAI & Knowledge Buddy
            - RPA & Workforce Intel
            """)
        with col4:
            st.markdown("""
            **🚀 DevOps & Security**
            - CI/CD & Deployment
            - Docker / Kubernetes
            - Authentication (LDAP/SSO)
            - Security alerts & auditing
            - Upgrade & migration
            """)

        st.divider()

        suggestions = st.container()
        with suggestions:
            st.markdown("#### 💡 Try one of these to get started:")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.button("🔴 What is PEGA0001?", use_container_width=True,
                           on_click=_send_question, args=("What does PEGA0001 alert mean and how to fix it?",))
            with col2:
                st.button("🔧 NullPointerException", use_container_width=True,
                           on_click=_send_question, args=("How to debug NullPointerException in Pega activity?",))
            with col3:
                st.button("⚡ Activity vs Data Transform", use_container_width=True,
                           on_click=_send_question, args=("When should I use Activity vs Data Transform?",))
            with col4:
                st.button("🔒 Auth Failures", use_container_width=True,
                           on_click=_send_question, args=("How to troubleshoot authentication failures in Pega?",))

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.button("📊 Explain Data Pages", use_container_width=True,
                           on_click=_send_question, args=("Explain Data Pages in Pega — what are they, scopes, and best practices?",))
            with col2:
                st.button("🤖 Pega RPA Overview", use_container_width=True,
                           on_click=_send_question, args=("Give me an overview of Pega Robotic Process Automation",))
            with col3:
                st.button("✨ Pega Constellation", use_container_width=True,
                           on_click=_send_question, args=("What is Pega Constellation UI architecture and how does it differ from Traditional UI?",))
            with col4:
                st.button("🧠 Pega GenAI & Blueprint", use_container_width=True,
                           on_click=_send_question, args=("What is Pega GenAI and Blueprint? Explain Knowledge Buddy, Autopilot, and how Blueprint works.",))
        # Clear the suggestions container once a button is clicked
        if st.session_state.messages:
            suggestions.empty()



# ── Chat Input (always at the bottom) ─────────────────────────────────
st.chat_input(
    "Ask PegaPal anything — errors, concepts, how-tos, comparisons...",
    key="user_chat_input",
    on_submit=_on_chat_submit,
)