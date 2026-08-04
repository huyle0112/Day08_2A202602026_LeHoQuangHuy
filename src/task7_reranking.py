"""Task 7 - Reciprocal Rank Fusion (RRF) for hybrid travel retrieval."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

RRF_K = 60


def _key(item: dict[str, Any]) -> tuple[str, str, str]:
    meta = item.get("metadata") or {}
    return (str(meta.get("source", "")), str(meta.get("chunk_index", "")), str(item.get("content", "")))


def rerank_rrf(ranked_lists: list[list[dict]], top_k: int = 5, k: int = RRF_K) -> list[dict]:
    """Fuse ranker outputs with ``sum(1 / (k + rank))``.

    The result score is an RRF ordering score, not a calibrated relevance score.
    """
    if top_k <= 0 or k < 0:
        return []
    scores: dict[tuple[str, str, str], float] = {}
    items: dict[tuple[str, str, str], dict] = {}
    for ranked_list in ranked_lists:
        for rank, candidate in enumerate(ranked_list or [], start=1):
            if not candidate.get("content"):
                continue
            identity = _key(candidate)
            scores[identity] = scores.get(identity, 0.0) + 1.0 / (k + rank)
            items.setdefault(identity, dict(candidate))
    ordered = sorted(scores, key=lambda identity: (-scores[identity], identity))[:top_k]
    return [{**items[identity], "score": round(scores[identity], 8), "rrf_score": round(scores[identity], 8)}
            for identity in ordered]


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[^\W_]+", text.lower(), flags=re.UNICODE))


def rerank(query: str, candidates: list[dict], top_k: int = 5, method: str = "rrf") -> list[dict]:
    """Rerank candidates deterministically without an external model.

    In the hybrid pipeline, use :func:`rerank_rrf` directly to combine dense
    and sparse lists.  This interface then promotes candidates that cover more
    query terms while retaining their incoming fusion rank as a tie-breaker.
    """
    if top_k <= 0:
        return []
    if method not in {"rrf", "lexical"}:
        raise ValueError("This lab implementation supports method='rrf' or 'lexical'.")
    query_terms = _tokens(query)
    rescored: list[dict] = []
    for position, candidate in enumerate(candidates or [], start=1):
        content_terms = _tokens(str(candidate.get("content", "")))
        coverage = len(query_terms & content_terms) / max(len(query_terms), 1)
        incoming = max(float(candidate.get("score", 0.0)), 0.0)
        # Candidate order is meaningful after RRF; normalize its contribution.
        rank_prior = 1.0 / (RRF_K + position)
        score = 0.75 * coverage + 0.20 * rank_prior + 0.05 * min(incoming, 1.0)
        rescored.append({**candidate, "score": round(score, 6), "rerank_score": round(score, 6)})
    return sorted(rescored, key=lambda item: item["score"], reverse=True)[:top_k]
