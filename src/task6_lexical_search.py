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
    global CORPUS, _TOKENS
    CORPUS = list(corpus)
    _TOKENS = [tokenize(str(item.get("content", ""))) for item in CORPUS]
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
    return [
        {"content": CORPUS[index]["content"], "score": round(float(score), 6),
         "metadata": dict(CORPUS[index].get("metadata", {}))}
        for index, score in ranked[:top_k] if float(score) > 0
    ]
