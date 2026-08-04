"""Task 6 - Sparse lexical retrieval for the travel-guide knowledge base.

BM25 is the primary ranker.  A small TF-IDF implementation is kept as a
dependency-free fallback so the retriever is still usable in a fresh lab
environment before ``rank-bm25`` has been installed.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CORPUS: list[dict[str, Any]] = []
_INDEX: Any | None = None
_TOKENS: list[list[str]] = []
_SIGNATURE: tuple[tuple[str, int], ...] = ()
_CHAR_VECTORIZER: Any | None = None
_CHAR_MATRIX: Any | None = None


def tokenize(text: str) -> list[str]:
    """Tokenize Vietnamese/English text without discarding accented letters."""
    return re.findall(r"[^\W_]+", text.lower(), flags=re.UNICODE)


def load_corpus() -> list[dict[str, Any]]:
    """Load Markdown guides and split each guide into readable retrieval units."""
    corpus: list[dict[str, Any]] = []
    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            continue
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
        # Group short paragraphs so navigation fragments do not dominate BM25.
        buffer: list[str] = []
        chunk_index = 0
        for paragraph in paragraphs:
            buffer.append(paragraph)
            if len("\n\n".join(buffer)) >= 700:
                corpus.append({"content": "\n\n".join(buffer), "metadata": {
                    "source": path.name, "type": path.parent.name, "chunk_index": chunk_index,
                }})
                buffer, chunk_index = [], chunk_index + 1
        if buffer:
            corpus.append({"content": "\n\n".join(buffer), "metadata": {
                "source": path.name, "type": path.parent.name, "chunk_index": chunk_index,
            }})
    return corpus


def _corpus_signature() -> tuple[tuple[str, int], ...]:
    return tuple((str(p.relative_to(STANDARDIZED_DIR)), p.stat().st_mtime_ns)
                 for p in sorted(STANDARDIZED_DIR.rglob("*.md"))) if STANDARDIZED_DIR.exists() else ()


def build_bm25_index(corpus: list[dict[str, Any]]):
    """Build and return a BM25Okapi index for ``corpus``."""
    global CORPUS, _TOKENS, _CHAR_VECTORIZER, _CHAR_MATRIX
    CORPUS = list(corpus)
    _TOKENS = [tokenize(str(item.get("content", ""))) for item in CORPUS]
    # Corpus đổi thì cache character TF-IDF cũng phải được dựng lại ở lần fallback kế tiếp.
    _CHAR_VECTORIZER = None
    _CHAR_MATRIX = None
    try:
        from rank_bm25 import BM25Okapi
    except ImportError:
        return None
    return BM25Okapi(_TOKENS)


def _ensure_index() -> None:
    global _INDEX, _SIGNATURE
    signature = _corpus_signature()
    if _INDEX is None or signature != _SIGNATURE:
        _INDEX = build_bm25_index(load_corpus())
        _SIGNATURE = signature


def _tfidf_scores(query_tokens: list[str]) -> list[float]:
    """Fallback sparse scoring if rank-bm25 is not available."""
    if not _TOKENS or not query_tokens:
        return [0.0] * len(_TOKENS)
    document_frequency = Counter(token for tokens in _TOKENS for token in set(tokens))
    query_counts = Counter(query_tokens)
    scores: list[float] = []
    for tokens in _TOKENS:
        counts = Counter(tokens)
        length = max(len(tokens), 1)
        score = sum((counts[token] / length) * (math.log((1 + len(_TOKENS)) / (1 + document_frequency[token])) + 1) * qtf
                    for token, qtf in query_counts.items())
        scores.append(score)
    return scores


def _char_tfidf_scores(query: str) -> list[float]:
    """Score fallback bằng character n-gram khi BM25 không có exact-token match.

    Character n-gram chịu được khác biệt dấu câu, biến thể từ và một phần khác biệt
    ngôn ngữ tốt hơn word-level BM25. Điểm này chỉ dùng để xếp hạng tương đối; Task 9
    vẫn dùng cosine score của dense retrieval để quyết định fallback ngoài domain.
    """
    global _CHAR_VECTORIZER, _CHAR_MATRIX
    if not CORPUS:
        return []

    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    if _CHAR_VECTORIZER is None or _CHAR_MATRIX is None:
        _CHAR_VECTORIZER = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            lowercase=True,
            min_df=1,
            sublinear_tf=True,
        )
        _CHAR_MATRIX = _CHAR_VECTORIZER.fit_transform(
            [str(item.get("content", "")) for item in CORPUS]
        )

    query_vector = _CHAR_VECTORIZER.transform([query])
    return cosine_similarity(query_vector, _CHAR_MATRIX).ravel().tolist()


def lexical_search(query: str, top_k: int = 10) -> list[dict[str, Any]]:
    """Return positively matched guide chunks, ranked by BM25 score descending."""
    if not isinstance(query, str) or not query.strip() or top_k <= 0:
        return []
    _ensure_index()
    query_tokens = tokenize(query)
    if not query_tokens:
        return []
    scores = _INDEX.get_scores(query_tokens) if _INDEX is not None else _tfidf_scores(query_tokens)
    ranked = sorted(enumerate(scores), key=lambda pair: (-float(pair[1]), pair[0]))
    primary_method = "bm25" if _INDEX is not None else "word_tfidf"
    selected = [
        (index, float(score), primary_method)
        for index, score in ranked
        if float(score) > 0
    ][:top_k]

    # Nếu lexical match quá ít, character TF-IDF chỉ bổ sung các vị trí còn thiếu.
    # Điểm bổ sung được scale thấp hơn BM25 nhỏ nhất để không đảo ưu tiên exact match.
    if len(selected) < top_k:
        fallback_scores = _char_tfidf_scores(query)
        fallback_ranked = sorted(
            ((index, float(score)) for index, score in enumerate(fallback_scores)
             if float(score) > 0),
            key=lambda pair: (-float(pair[1]), pair[0]),
        )
        selected_indices = {index for index, _, _ in selected}
        fallback_ranked = [
            (index, score) for index, score in fallback_ranked
            if index not in selected_indices
        ]
        missing = top_k - len(selected)
        fallback_ranked = fallback_ranked[:missing]

        if selected and fallback_ranked:
            max_fallback = fallback_ranked[0][1]
            ceiling = min(score for _, score, _ in selected) * 0.5
            fallback_ranked = [
                (index, (score / max_fallback) * ceiling)
                for index, score in fallback_ranked
            ]

        selected.extend(
            (index, score, "char_tfidf_fallback")
            for index, score in fallback_ranked
        )

    selected.sort(key=lambda item: (-item[1], item[0]))

    return [
        {"content": CORPUS[index]["content"], "score": round(float(score), 6),
         "metadata": {**dict(CORPUS[index].get("metadata", {})),
                      "retrieval_method": retrieval_method}}
        for index, score, retrieval_method in selected[:top_k]
    ]
