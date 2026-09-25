"""Reciprocal rank fusion: merge ranked lists using only their positions."""

from rag.store import Hit


def rrf(*rankings: list[Hit], k: int = 60) -> list[Hit]:
    """Merge any number of ranked lists into one.

    Each list contributes 1 / (k + rank) for every hit it contains, and a hit
    that appears in several lists adds its contributions up. Scores are never
    consulted, only positions, which is what lets a BM25 list and a cosine list
    be combined at all: their scores are on unrelated scales.
    """

    scores: dict[str, float] = {}
    hits: dict[str, Hit] = {}

    for ranking in rankings:
        for rank, hit in enumerate(ranking, start=1):
            key = f"{hit.source}:{hit.position}"
            scores[key] = scores.get(key, 0.0) + 1 / (k + rank)
            hits.setdefault(key, hit)
    return [
        hits[key] for key in sorted(scores, key=lambda key: scores[key], reverse=True)
    ]
