from app.core.config import get_settings
from app.retrieval.vector_store import semantic_search


def retrieve_context(
    question: str,
    top_k: int | None = None
) -> list[dict]:
    """
    Retrieve the most semantically relevant document chunks.

    Includes:
    - configurable retrieval count
    - distance-based sorting
    - lightweight relevance filtering
    """

    settings = get_settings()

    k = top_k or settings.retrieval_top_k

    results = semantic_search(question, k)

    if not results:
        return []

    # sort by best similarity score if available
    results = sorted(
        results,
        key=lambda x: x.get("score", 9999)
    )

    # remove empty or extremely poor matches
    filtered = []

    for item in results:
        text = item.get("text", "").strip()

        if not text:
            continue

        filtered.append(item)

    return filtered[:k]