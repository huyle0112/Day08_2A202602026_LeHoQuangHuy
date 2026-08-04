"""
Task 4 — Chunking & Indexing vào Vector Store.

Hướng dẫn:
    1. Đọc toàn bộ markdown files từ data/standardized/
    2. Chọn 1 chunking strategy (giải thích lý do)
    3. Chọn 1 embedding model (giải thích lý do)
    4. Index vào vector store (ChromaDB khuyến cáo — đơn giản, local, không cần Docker)

Chunking options (langchain-text-splitters):
    - RecursiveCharacterTextSplitter: an toàn, phổ biến
    - MarkdownHeaderTextSplitter: tốt cho file có heading
    - SemanticChunker: dùng embedding để tách (nâng cao)

Embedding model options (chọn 1, cân nhắc đánh đổi cài đặt nặng vs cần API key):
    - sentence-transformers/all-MiniLM-L6-v2 hoặc BAAI/bge-m3 — chạy local, không
      cần API key, nhưng cài nặng (~1-2GB vì kéo theo torch)
    - Google models/text-embedding-004 (768 dim) — nhẹ, cần GEMINI_API_KEY
    - OpenAI text-embedding-3-small (1536 dim) — nhẹ, cần OPENAI_API_KEY
    Gợi ý: đọc EMBEDDING_PROVIDER từ .env (os.getenv("EMBEDDING_PROVIDER", "sentence_transformers"))
    để cả nhóm có thể đổi provider mà không sửa code — nhớ đổi provider phải xoá
    chroma_db/ cũ và reindex vì dimension khác nhau (1024/768/1536) không tương thích ngược.

Vector store options:
    - ChromaDB (khuyến cáo: đơn giản, local persistent, không cần Docker)
    - Weaviate (hỗ trợ hybrid search built-in, cần Docker/Cloud)
    - FAISS (chỉ dense search)

Cài đặt:
    pip install langchain-text-splitters sentence-transformers chromadb

Lưu ý quan trọng: nếu sau này đổi corpus (đổi chủ đề, thêm/bớt tài liệu), phải XÓA
chroma_db/ cũ trước khi reindex — nếu không, chunk cũ và mới sẽ tồn tại lẫn lộn
trong cùng collection, retrieval sẽ trả về kết quả rác từ dữ liệu cũ.
"""

import hashlib
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"


# =============================================================================
# CONFIGURATION — Giải thích lựa chọn của bạn trong comment
# =============================================================================

# RecursiveCharacterTextSplitter giữ được ranh giới đoạn/câu khi có thể, nhưng vẫn bảo
# đảm giới hạn kích thước với tài liệu Markdown không đồng nhất từ nhiều nguồn.
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
CHUNKING_METHOD = "recursive"  # "recursive" | "markdown_header" | "semantic"

# OpenAI embedding không cần cài PyTorch/model local, hỗ trợ tốt tiếng Việt và tạo vector
# 1536 chiều đủ gọn cho corpus của bài lab.
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai").strip().lower()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small").strip()
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1536"))
EMBEDDING_BATCH_SIZE = 64

VECTOR_STORE = "chromadb"  # "chromadb" | "weaviate" | "faiss"
COLLECTION_NAME = "northern_vietnam_travel_docs"


# =============================================================================
# IMPLEMENTATION
# =============================================================================

def load_documents() -> list[dict]:
    """
    Đọc toàn bộ markdown files từ data/standardized/.

    Returns:
        List of {'content': str, 'metadata': {'source': str, 'type': str}}
    """
    if not STANDARDIZED_DIR.exists():
        return []

    documents = []
    for md_file in sorted(STANDARDIZED_DIR.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8").strip()
        if not content:
            continue

        relative_path = md_file.relative_to(STANDARDIZED_DIR)
        doc_type = relative_path.parts[0] if len(relative_path.parts) > 1 else "unknown"
        documents.append({
            "content": content,
            "metadata": {
                "source": md_file.name,
                "source_path": relative_path.as_posix(),
                "type": doc_type,
            },
        })
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Chunk documents theo strategy đã chọn.

    Returns:
        List of {'content': str, 'metadata': dict} — mỗi item là 1 chunk
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", "; ", ", ", " ", ""],
    )

    chunks = []
    for doc in documents:
        content = str(doc.get("content", "")).strip()
        if not content:
            continue
        metadata = dict(doc.get("metadata", {}))
        for chunk_index, chunk_text in enumerate(splitter.split_text(content)):
            chunk_text = chunk_text.strip()
            if not chunk_text:
                continue
            chunks.append({
                "content": chunk_text,
                "metadata": {**metadata, "chunk_index": chunk_index},
            })
    return chunks


def _openai_client():
    """Khởi tạo OpenAI client và báo lỗi cấu hình rõ ràng."""
    if EMBEDDING_PROVIDER != "openai":
        raise ValueError(
            "Cấu hình Role 2 hiện dùng OpenAI cloud; hãy đặt EMBEDDING_PROVIDER=openai."
        )
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Thiếu OPENAI_API_KEY trong file .env hoặc biến môi trường.")

    from openai import OpenAI

    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Tạo embedding theo batch để Task 4 và Task 5 dùng chung đúng một model."""
    if not texts:
        return []
    if any(not isinstance(text, str) or not text.strip() for text in texts):
        raise ValueError("Mỗi nội dung cần embedding phải là chuỗi không rỗng.")

    client = _openai_client()
    embeddings: list[list[float]] = []
    for start in range(0, len(texts), EMBEDDING_BATCH_SIZE):
        batch = texts[start:start + EMBEDDING_BATCH_SIZE]
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
            dimensions=EMBEDDING_DIM,
        )
        ordered = sorted(response.data, key=lambda item: item.index)
        embeddings.extend(item.embedding for item in ordered)

    if len(embeddings) != len(texts):
        raise RuntimeError("OpenAI trả về số embedding không khớp số văn bản đầu vào.")
    return embeddings


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    Embed toàn bộ chunks bằng model đã chọn.

    Returns:
        Mỗi chunk dict được thêm key 'embedding': list[float]
    """
    embeddings = embed_texts([chunk["content"] for chunk in chunks])
    return [
        {**chunk, "embedding": embedding}
        for chunk, embedding in zip(chunks, embeddings)
    ]


def get_collection():
    """Mở (hoặc khởi tạo) collection ChromaDB persistent dùng cosine distance."""
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "hnsw:space": "cosine",
            "embedding_provider": EMBEDDING_PROVIDER,
            "embedding_model": EMBEDDING_MODEL,
            "embedding_dimension": EMBEDDING_DIM,
        },
    )


def index_to_vectorstore(chunks: list[dict]):
    """
    Lưu chunks vào vector store đã chọn.
    """
    if not chunks:
        return get_collection()
    if any("embedding" not in chunk for chunk in chunks):
        raise ValueError("Chunks chưa có embedding; hãy gọi embed_chunks() trước.")

    collection = get_collection()
    ids = []
    for chunk in chunks:
        metadata = chunk.get("metadata", {})
        identity = "|".join([
            str(metadata.get("source_path", metadata.get("source", "unknown"))),
            str(metadata.get("chunk_index", 0)),
            chunk["content"],
        ])
        ids.append(hashlib.sha256(identity.encode("utf-8")).hexdigest())

    collection.upsert(
        ids=ids,
        documents=[chunk["content"] for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        metadatas=[chunk.get("metadata", {}) for chunk in chunks],
    )
    return collection


def run_pipeline():
    """Chạy toàn bộ pipeline: load → chunk → embed → index."""
    print("=" * 50)
    print("Task 4: Chunking & Indexing")
    print(f"  Chunking: {CHUNKING_METHOD} (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    print(f"  Embedding: {EMBEDDING_PROVIDER}/{EMBEDDING_MODEL} (dim={EMBEDDING_DIM})")
    print(f"  Vector Store: {VECTOR_STORE}")
    print("=" * 50)

    docs = load_documents()
    print(f"\n✓ Loaded {len(docs)} documents")

    chunks = chunk_documents(docs)
    print(f"✓ Created {len(chunks)} chunks")

    chunks = embed_chunks(chunks)
    print(f"✓ Embedded {len(chunks)} chunks")

    collection = index_to_vectorstore(chunks)
    print(f"✓ Indexed to vector store ({collection.count()} records)")


if __name__ == "__main__":
    run_pipeline()
