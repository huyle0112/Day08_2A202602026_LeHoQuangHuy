"""Task 8 - PageIndex-style vectorless fallback for travel guides.

The fallback navigates natural document sections (title -> section -> content),
not embeddings or a vector database.  It works locally for the lab and can be
replaced by the hosted PageIndex API after uploading the PDF files.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
_TREE_CACHE: list[dict[str, Any]] | None = None
_CACHE_SIGNATURE: tuple[tuple[str, int], ...] = ()


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[^\W_]+", text.lower(), flags=re.UNICODE))


def _signature() -> tuple[tuple[str, int], ...]:
    if not STANDARDIZED_DIR.exists():
        return ()
    return tuple((str(path.relative_to(STANDARDIZED_DIR)), path.stat().st_mtime_ns)
                 for path in sorted(STANDARDIZED_DIR.rglob("*.md")))


def _looks_like_heading(line: str) -> bool:
    """Recognize Markdown headings plus common headings in converted PDFs."""
    text = line.strip()
    return bool(
        text.startswith("#")
        or re.match(r"^(?:\d+[.)]|[IVXLC]+[.)])\s+", text)
        or (len(text) <= 110 and (text.endswith("?") or ":" in text))
    )


def build_pageindex_tree() -> list[dict[str, Any]]:
    """Build a lightweight, inspectable document tree from Markdown guides."""
    global _TREE_CACHE, _CACHE_SIGNATURE
    signature = _signature()
    if _TREE_CACHE is not None and signature == _CACHE_SIGNATURE:
        return _TREE_CACHE

    tree: list[dict[str, Any]] = []
    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        document_title = next((line.strip() for line in lines if line.strip()), path.stem)
        section_title = document_title
        section_lines: list[str] = []

        def append_section() -> None:
            content = "\n".join(section_lines).strip()
            if len(content) >= 80:
                tree.append({
                    "title": section_title,
                    "content": content,
                    "metadata": {"source": path.name, "type": path.parent.name,
                                 "document_title": document_title},
                })

        for line in lines:
            if _looks_like_heading(line) and section_lines:
                append_section()
                section_lines = []
                section_title = line.strip().lstrip("#").strip()
            else:
                section_lines.append(line)
        append_section()
    _TREE_CACHE, _CACHE_SIGNATURE = tree, signature
    return tree


def upload_documents() -> list[str]:
    """Return the PDFs that should be uploaded in the PageIndex dashboard.

    Cloud API contracts change frequently; for this lab, upload the returned
    paths in the dashboard, then retain the supplied document IDs in `.env`.
    Local ``pageindex_search`` remains fully functional without credentials.
    """
    pdf_dir = Path(__file__).parent.parent / "data" / "landing" / "legal"
    return [str(path) for path in sorted(pdf_dir.rglob("*.pdf"))]


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Vectorless fallback using section-tree navigation.

    Scores are lexical section-relevance scores only for ordering. They are
    deliberately separate from dense cosine scores used by Task 9's threshold.
    """
    if not isinstance(query, str) or not query.strip() or top_k <= 0:
        return []
    query_terms = _tokens(query)
    if not query_terms:
        return []

    results: list[dict] = []
    for node in build_pageindex_tree():
        title_terms = _tokens(node["title"])
        content_terms = _tokens(node["content"])
        title_overlap = len(query_terms & title_terms) / len(query_terms)
        content_overlap = len(query_terms & content_terms) / len(query_terms)
        score = 0.7 * title_overlap + 0.3 * content_overlap
        if score > 0:
            results.append({
                "content": node["content"],
                "score": round(score, 6),
                "metadata": {**node["metadata"], "section": node["title"],
                             "engine": "local_pageindex_tree"},
                "source": "pageindex",
            })
    results.sort(key=lambda item: (-item["score"], item["metadata"]["source"]))
    return results[:top_k]


if __name__ == "__main__":
    for result in pageindex_search("lich trinh Ha Giang xe may", top_k=3):
        print(f"[{result['score']:.3f}] {result['metadata']['section']}")
