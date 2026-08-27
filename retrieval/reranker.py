def rerank(
    results,
    top_k,
    max_distance=0.65
):
    """
    Keep only reasonably relevant results.

    Lower Chroma distance means greater similarity.

    The threshold is intentionally configurable
    because the right value depends on the embedding
    model and document collection.
    """

    if not results:
        return []

    relevant = [
        result
        for result in results
        if result.get(
            "distance",
            float("inf")
        ) <= max_distance
    ]

    relevant.sort(
        key=lambda item: item.get(
            "distance",
            float("inf")
        )
    )

    return relevant[:top_k]