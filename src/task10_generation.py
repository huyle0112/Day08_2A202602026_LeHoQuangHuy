"""
Task 10 — Generation Có Citation cho trợ lý du lịch miền Bắc Việt Nam.

Hướng dẫn:
    1. Chọn top_k, top_p phù hợp (giải thích lý do)
    2. Sắp xếp lại chunks sau reranking để tránh "lost in the middle"
    3. Inject context vào prompt
    4. Yêu cầu LLM trả lời có citation
    5. Nếu không đủ evidence → "I cannot verify this information"

LLM và embedding đều dùng OpenAI API để thống nhất cấu hình cloud của nhóm.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from .task9_retrieval_pipeline import retrieve


# =============================================================================
# CONFIGURATION — Giải thích lựa chọn
# =============================================================================

# top_k: Số chunks đưa vào context
# Chọn 5 vì: đủ evidence mà không quá dài gây lost in the middle
TOP_K = 5

# top_p (nucleus sampling): Xác suất tích luỹ cho token generation
# Chọn 0.9 vì: đủ diverse nhưng không quá random
TOP_P = 0.9

# temperature: Độ ngẫu nhiên của output
# Chọn 0.3 vì: RAG cần factual, ít sáng tạo
TEMPERATURE = 0.3

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()


# =============================================================================
# SYSTEM PROMPT
# =============================================================================

SYSTEM_PROMPT = """Bạn là trợ lý hướng dẫn du lịch thông minh cho 10 tỉnh/thành miền Bắc
Việt Nam: Hà Nội, Hà Giang, Ninh Bình, Quảng Ninh, Lào Cai, Cao Bằng, Sơn La,
Lạng Sơn, Yên Bái và Hải Phòng.

Quy tắc bắt buộc:
1. Chỉ sử dụng thông tin từ context được cung cấp — KHÔNG bịa đặt
2. Mỗi khẳng định phải có trích dẫn ngay sau, dùng đúng tên Source trong context
3. Nếu context không đủ thông tin → trả lời: "Tôi không thể xác minh thông tin này từ nguồn hiện có"
4. Trả lời bằng tiếng Việt, có cấu trúc rõ ràng theo đoạn văn
5. Không suy luận hay mở rộng ngoài những gì được nêu trong context"""


# =============================================================================
# DOCUMENT REORDERING (tránh lost in the middle)
# =============================================================================

def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """
    Sắp xếp chunks để tránh "lost in the middle" effect.

    LLM nhớ tốt thông tin ở ĐẦU và CUỐI prompt, quên thông tin ở GIỮA.
    Strategy: đặt chunks quan trọng nhất ở đầu và cuối, kém quan trọng ở giữa.

    Input order (by score):  [1, 2, 3, 4, 5]
    Output order:            [1, 3, 5, 4, 2]
    (best first, worst in middle, second-best last)

    Args:
        chunks: List sorted by score descending (from retrieval)

    Returns:
        List reordered để maximize LLM attention.
    """
    if len(chunks) <= 2:
        return list(chunks)
    front = chunks[::2]
    back = chunks[1::2]
    return front + back[::-1]


# =============================================================================
# CONTEXT FORMATTING
# =============================================================================

def format_context(chunks: list[dict]) -> str:
    """
    Format chunks thành context string cho prompt.
    Mỗi chunk có label source để LLM có thể cite.

    Args:
        chunks: List of {'content': str, 'metadata': dict, 'score': float}

    Returns:
        Formatted context string.
    """
    context_parts = []
    for index, chunk in enumerate(chunks, start=1):
        metadata = chunk.get("metadata") or {}
        source = str(metadata.get("source") or f"Source {index}")
        doc_type = str(metadata.get("type") or "unknown")
        content = str(chunk.get("content") or "").strip()
        if not content:
            continue
        context_parts.append(
            f"[Document {index} | Source: {source} | Type: {doc_type}]\n{content}"
        )
    return "\n\n---\n\n".join(context_parts)


def _safe_generation_fallback(chunks: list[dict], reason: str) -> str:
    """Phản hồi không bịa đặt khi OpenAI tạm thời không khả dụng."""
    if not chunks:
        return "Tôi không thể xác minh thông tin này từ nguồn hiện có."
    sources = []
    for chunk in chunks:
        source = str((chunk.get("metadata") or {}).get("source") or "Nguồn không xác định")
        if source not in sources:
            sources.append(source)
    source_labels = ", ".join(f"[{source}]" for source in sources[:3])
    return (
        "Hiện chưa thể gọi mô hình để tổng hợp câu trả lời. "
        f"Các nguồn liên quan đã truy xuất: {source_labels}. "
        f"Chi tiết kỹ thuật: {reason}"
    )


# =============================================================================
# GENERATION
# =============================================================================

def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """
    End-to-end RAG generation có citation.

    Pipeline:
        1. Retrieve relevant chunks
        2. Reorder để tránh lost in the middle
        3. Format context với source labels
        4. Build prompt (system + context + query)
        5. Call LLM
        6. Return answer + sources

    Args:
        query: Câu hỏi của user

    Returns:
        {
            'answer': str,           # Câu trả lời có citation
            'sources': list[dict],   # Các chunks đã dùng
            'retrieval_source': str  # 'hybrid' hoặc 'pageindex'
        }
    """
    if not isinstance(query, str) or not query.strip():
        return {
            "answer": "Vui lòng nhập câu hỏi du lịch cần tra cứu.",
            "sources": [],
            "retrieval_source": "none",
        }
    if top_k <= 0:
        return {
            "answer": "Tôi không thể xác minh thông tin này từ nguồn hiện có.",
            "sources": [],
            "retrieval_source": "none",
        }

    chunks = retrieve(query.strip(), top_k=top_k)
    retrieval_source = chunks[0].get("source", "hybrid") if chunks else "none"
    if not chunks:
        return {
            "answer": "Tôi không thể xác minh thông tin này từ nguồn hiện có.",
            "sources": [],
            "retrieval_source": retrieval_source,
        }

    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    user_message = f"Context:\n{context}\n\n---\n\nCâu hỏi: {query.strip()}"

    if not os.getenv("OPENAI_API_KEY"):
        answer = _safe_generation_fallback(chunks, "thiếu OPENAI_API_KEY")
    else:
        try:
            from openai import OpenAI, OpenAIError

            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=TEMPERATURE,
                top_p=TOP_P,
            )
            answer = (response.choices[0].message.content or "").strip()
            if not answer:
                answer = _safe_generation_fallback(chunks, "mô hình trả về nội dung rỗng")
        except OpenAIError as exc:
            answer = _safe_generation_fallback(chunks, exc.__class__.__name__)

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": retrieval_source,
    }


if __name__ == "__main__":
    test_queries = [
        "Nên đi Hà Giang vào mùa nào?",
        "Gợi ý lịch trình khám phá Ninh Bình trong hai ngày.",
        "Các điểm tham quan nổi bật tại Cao Bằng là gì?",
    ]

    for q in test_queries:
        print(f"\n{'='*70}")
        print(f"Q: {q}")
        print("=" * 70)
        result = generate_with_citation(q)
        print(f"\nA: {result['answer']}")
        print(f"\n[Sources: {len(result['sources'])} chunks | via {result['retrieval_source']}]")
