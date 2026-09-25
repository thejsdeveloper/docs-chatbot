"""Second stage: score every candidate against the question and reorder.

The reranker reads the question and the chunk together, which is what the
embedding search could not afford to do for ten thousand chunks. It is only
worth running on a shortlist, so `candidates` is the fused list, not the store.
"""

import os

import httpx
from dotenv import load_dotenv

from rag.constants import OPENROUTER_BASE_URL, RERANK_MODEL
from rag.store import Hit

load_dotenv()


def rerank(question: str, candidates: list[Hit], k: int) -> list[Hit]:
    if not candidates:
        return []
    response = httpx.post(
        f"{OPENROUTER_BASE_URL}/rerank",
        headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
        json={
            "model": RERANK_MODEL,
            "query": question,
            "documents": [hit.text for hit in candidates],
            "top_n": k,
        },
        timeout=30,
    )

    response.raise_for_status()
    # `results` comes back best first, each carrying the index of the
    # document it scored, so the reorder is one lookup per result.
    return [candidates[result["index"]] for result in response.json()["results"]]
