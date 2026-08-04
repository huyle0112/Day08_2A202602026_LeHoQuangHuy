"""
Task 5 — Semantic Search Module.

Viết module tìm kiếm ngữ nghĩa (dense retrieval) trên vector store.

Yêu cầu:
    - Input: query string + top_k
    - Output: danh sách chunks có score, sorted descending
    - Phải tương thích với embedding model và vector store ở Task 4
"""

import os

from dotenv import load_dotenv

from .task4_chunking_indexing import embed_texts, get_collection

load_dotenv()

HYDE_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()


def generate_hypothetical_document(query: str) -> str:
    """Dùng LLM tạo một đoạn tài liệu giả định giàu ngữ nghĩa cho HyDE retrieval."""
    if not query or not query.strip():
        raise ValueError("Query không được để trống.")
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Thiếu OPENAI_API_KEY để sử dụng HyDE.")

    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model=HYDE_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Bạn hỗ trợ truy xuất tài liệu du lịch miền Bắc Việt Nam. "
                    "Hãy viết một đoạn tài liệu giả định ngắn chứa thông tin và từ khóa "
                    "có khả năng xuất hiện trong nguồn liên quan. Không cần trích dẫn và "
                    "không khẳng định đây là câu trả lời đã được kiểm chứng."
                ),
            },
            {"role": "user", "content": query.strip()},
        ],
        temperature=0.2,
    )
    hypothetical_document = response.choices[0].message.content or ""
    if not hypothetical_document.strip():
        raise RuntimeError("OpenAI không trả về nội dung HyDE.")
    return hypothetical_document.strip()


def semantic_search(query: str, top_k: int = 10, use_hyde: bool = False) -> list[dict]:
    """
    Tìm kiếm ngữ nghĩa sử dụng vector similarity.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,      # Nội dung chunk
            'score': float,      # Cosine similarity score
            'metadata': dict     # source, doc_type, chunk_index
        }
        Sorted by score descending.
    """
    if not query or not query.strip():
        return []
    if top_k <= 0:
        return []

    collection = get_collection()
    available = collection.count()
    if available == 0:
        return []

    embedding_text = query.strip()
    if use_hyde:
        hypothetical_document = generate_hypothetical_document(query)
        # Giữ query gốc để không làm mất tên riêng; đoạn giả định bổ sung ngữ cảnh và từ đồng nghĩa.
        embedding_text = f"Câu hỏi: {query.strip()}\n\nTài liệu giả định:\n{hypothetical_document}"

    query_vector = embed_texts([embedding_text])[0]
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(top_k, available),
        include=["documents", "metadatas", "distances"],
    )

    documents = (results.get("documents") or [[]])[0]
    metadatas = (results.get("metadatas") or [[]])[0]
    distances = (results.get("distances") or [[]])[0]
    output = []
    for document, metadata, distance in zip(documents, metadatas, distances):
        output.append({
            "content": document,
            "score": round(1.0 - float(distance), 4),
            "metadata": metadata or {},
        })

    output.sort(key=lambda item: item["score"], reverse=True)
    return output[:top_k]


def hyde_search(query: str, top_k: int = 10) -> list[dict]:
    """Shortcut rõ nghĩa cho Dense Search dùng Hypothetical Document Embeddings."""
    return semantic_search(query, top_k=top_k, use_hyde=True)


if __name__ == "__main__":
    # Test
    results = semantic_search("Lịch trình du lịch Hà Giang 3 ngày", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")
