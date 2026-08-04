"""
RAG Chatbot — Trợ Lý Du Lịch Miền Bắc Việt Nam
Streamlit app kết nối RAG Retrieval (Task 9) và Generation (Task 10).

Giao diện: Glassmorphism, tông màu trung tính sang trọng (lấy cảm hứng
real-estate premium) — thẻ kính mờ, khoảng trắng rộng rãi, điểm nhấn vàng đồng.

Chạy:
    streamlit run app.py
"""

import html
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Thêm project root vào sys.path để import các task từ src/
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="Trợ Lý Du Lịch Miền Bắc RAG Chatbot",
    page_icon="🏞️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# GLASSMORPHISM THEME — Elegant / Premium / Trustworthy / Spacious / Neutral
# =============================================================================

GLASS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --glass-bg: rgba(255, 255, 255, 0.55);
    --glass-bg-strong: rgba(255, 255, 255, 0.75);
    --glass-border: rgba(255, 255, 255, 0.65);
    --ink: #2b2621;
    --ink-soft: #746a5d;
    --accent: #a9825a;
    --accent-soft: rgba(169, 130, 90, 0.14);
}

html, body, [data-testid="stAppViewContainer"], [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--ink);
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 10% 6%, rgba(255, 246, 230, 0.95), transparent 40%),
        radial-gradient(circle at 90% 10%, rgba(214, 202, 224, 0.5), transparent 42%),
        radial-gradient(circle at 50% 105%, rgba(233, 219, 197, 0.7), transparent 55%),
        linear-gradient(160deg, #f8f4ed 0%, #ede5d7 45%, #e4dac9 100%);
    background-attachment: fixed;
}

[data-testid="stHeader"] { background: transparent; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(255,255,255,0.55), rgba(255,255,255,0.30));
    backdrop-filter: blur(24px) saturate(140%);
    -webkit-backdrop-filter: blur(24px) saturate(140%);
    border-right: 1px solid var(--glass-border);
}

[data-testid="stSidebar"] h1, h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    letter-spacing: 0.01em;
}

.block-container {
    padding-top: 2.6rem;
    padding-bottom: 3rem;
    max-width: 920px;
}

h1 {
    font-weight: 600 !important;
    background: linear-gradient(120deg, #6b5236, #a9825a 55%, #6b5236);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-card {
    background: var(--glass-bg);
    backdrop-filter: blur(22px) saturate(150%);
    -webkit-backdrop-filter: blur(22px) saturate(150%);
    border: 1px solid var(--glass-border);
    border-radius: 28px;
    padding: 2rem 2.4rem;
    margin-bottom: 1.8rem;
    box-shadow: 0 12px 40px rgba(43, 38, 33, 0.08);
}
.hero-card .eyebrow {
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 0.16em;
    font-size: 0.72rem;
    font-weight: 600;
    margin-bottom: 0.4rem;
}
.hero-card h1 { margin: 0 0 0.4rem 0; font-size: 2.1rem; }
.hero-card p { color: var(--ink-soft); font-size: 0.98rem; margin: 0; }

/* Chat bubbles */
[data-testid="stChatMessage"] {
    background: var(--glass-bg) !important;
    backdrop-filter: blur(18px) saturate(160%);
    -webkit-backdrop-filter: blur(18px) saturate(160%);
    border: 1px solid var(--glass-border);
    border-radius: 20px !important;
    box-shadow: 0 8px 30px rgba(43, 38, 33, 0.07);
    padding: 0.5rem 0.7rem;
    margin-bottom: 1.1rem;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    border-left: 3px solid var(--accent);
    background: var(--glass-bg-strong) !important;
}

/* Buttons — pill, glass, gold on hover */
.stButton > button {
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    border-radius: 999px;
    color: var(--ink);
    font-weight: 500;
    padding: 0.55rem 1.1rem;
    box-shadow: 0 4px 14px rgba(43, 38, 33, 0.05);
    transition: all 0.22s ease;
}
.stButton > button:hover {
    border-color: var(--accent);
    color: var(--accent);
    box-shadow: 0 8px 22px rgba(169, 130, 90, 0.22);
    transform: translateY(-1px);
}

/* Chat input footer — must be styled too, not just the pill itself,
   otherwise Streamlit's own light/dark background shows through as a
   plain bar behind it. */
[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] > div {
    background: transparent !important;
}
[data-testid="stBottom"] {
    background: linear-gradient(0deg, rgba(248,244,237,0.96), rgba(248,244,237,0.0)) !important;
}
[data-testid="stChatInput"] {
    background: var(--glass-bg-strong);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 999px;
    box-shadow: 0 10px 30px rgba(43, 38, 33, 0.09);
}
[data-testid="stChatInput"] textarea {
    color: var(--ink) !important;
}

/* Expander (nguồn tham khảo) */
[data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.38);
    backdrop-filter: blur(14px);
    border: 1px solid var(--glass-border);
    border-radius: 18px;
    box-shadow: 0 4px 18px rgba(43, 38, 33, 0.05);
}

/* Source citation cards */
.source-card {
    background: rgba(255, 255, 255, 0.55);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 0.9rem 1.1rem;
    margin: 0.6rem 0;
}
.source-card-head {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-bottom: 0.4rem;
}
.source-badge {
    background: var(--accent);
    color: #fff;
    font-size: 0.72rem;
    font-weight: 600;
    border-radius: 999px;
    padding: 0.15rem 0.55rem;
}
.source-name { font-weight: 600; color: var(--ink); }
.source-type, .source-score {
    background: var(--accent-soft);
    color: var(--accent);
    font-size: 0.75rem;
    border-radius: 999px;
    padding: 0.1rem 0.55rem;
}
.source-snippet {
    color: var(--ink-soft);
    font-size: 0.88rem;
    line-height: 1.5;
    margin: 0;
}

hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(169,130,90,0.45), transparent);
    margin: 1.4rem 0;
}

[data-testid="stSlider"] [role="slider"] { background-color: var(--accent) !important; }

::-webkit-scrollbar { width: 10px; }
::-webkit-scrollbar-thumb { background: rgba(169,130,90,0.35); border-radius: 10px; }
::-webkit-scrollbar-track { background: transparent; }
</style>
"""
st.markdown(GLASS_CSS, unsafe_allow_html=True)


def render_sources(sources: list[dict]) -> None:
    """Hiển thị danh sách nguồn tham khảo dạng thẻ kính (glass card)."""
    with st.expander(f"📚 Nguồn tham khảo ({len(sources)} chunks)"):
        for i, src in enumerate(sources, 1):
            meta = src.get("metadata", {})
            source_name = html.escape(str(meta.get("source", "Unknown")))
            doc_type = html.escape(str(meta.get("type", "unknown")))
            score = src.get("score", 0)
            snippet = html.escape(str(src.get("content", ""))[:300])
            st.markdown(
                f"""
                <div class="source-card">
                    <div class="source-card-head">
                        <span class="source-badge">#{i}</span>
                        <span class="source-name">{source_name}</span>
                        <span class="source-type">{doc_type}</span>
                        <span class="source-score">score {score:.4f}</span>
                    </div>
                    <p class="source-snippet">{snippet}...</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =============================================================================
# SIDEBAR — INFO & SETTINGS
# =============================================================================

with st.sidebar:
    st.title("🏞️ Trợ Lý Du Lịch Miền Bắc")
    st.caption("Trợ lý hỏi đáp về lịch trình, điểm đến và kinh nghiệm du lịch miền Bắc Việt Nam")

    st.divider()

    st.subheader("💡 Câu hỏi gợi ý")
    suggestions = [
        "Con đèo nào nổi tiếng nhất khi đến Hà Giang?",
        "Thời điểm nào đẹp nhất để ngắm hoa tam giác mạch ở Hà Giang?",
        "Nên đi Sapa bằng phương tiện gì?",
        "Khu du lịch Tràng An ở Ninh Bình có mấy tuyến đò?",
        "Thời điểm lý tưởng để đi du lịch biển Đồ Sơn là khi nào?",
    ]
    for s in suggestions:
        if st.button(s, use_container_width=True, key=f"sug_{s[:20]}"):
            st.session_state["pending_query"] = s

    st.divider()
    st.subheader("⚙️ Thiết lập")
    top_k = st.slider("Số chunks retrieval (top_k)", 3, 10, 5)

    st.divider()
    st.caption("**Kiến trúc hệ thống:**")
    st.caption("Hybrid Retrieval (Semantic + BM25) → RRF Rerank → PageIndex Fallback → LLM Generation có Citation")

# =============================================================================
# SESSION STATE
# =============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# =============================================================================
# MAIN CHAT AREA
# =============================================================================

st.markdown(
    """
    <div class="hero-card">
        <div class="eyebrow">RAG Pipeline v2 · Hybrid Retrieval + Citation</div>
        <h1>🏞️ Trợ Lý Du Lịch Miền Bắc</h1>
        <p>Hệ thống hỏi đáp về lịch trình, điểm đến và kinh nghiệm du lịch miền Bắc Việt Nam — luôn kèm trích dẫn nguồn đáng tin cậy.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "sources" in msg and msg["sources"]:
            render_sources(msg["sources"])

# =============================================================================
# QUERY HANDLING
# =============================================================================

user_input = st.chat_input("Nhập câu hỏi của bạn về du lịch miền Bắc...")
query = user_input or st.session_state.pending_query

if query:
    st.session_state.pending_query = None

    # Hiển thị câu hỏi của user
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Sinh câu trả lời từ RAG Pipeline
    with st.chat_message("assistant"):
        with st.spinner("Đang tìm kiếm tài liệu và tổng hợp câu trả lời..."):
            try:
                from src.task10_generation import generate_with_citation
                response = generate_with_citation(query, top_k=top_k)
                answer = response.get("answer", "Chưa thể trả lời.")
                sources = response.get("sources", [])

            except NotImplementedError:
                answer = "⚠️ **Task 10 chưa được implement.** Hãy hoàn thành `src/task10_generation.py` để kết nối pipeline vào UI!"
                sources = []
            except Exception as e:
                answer = f"❌ **Lỗi khi chạy RAG Pipeline:** {e}"
                sources = []

            st.markdown(answer)

            if sources:
                render_sources(sources)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })
