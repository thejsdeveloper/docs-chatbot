"""One entry point for every retrieval strategy, so they can be compared."""

from typing import Literal

import chromadb

from rag import rerank
from rag.constants import CANDIDATE_K
from rag.fusion import rrf
from rag.lexical import get_index
from rag.rerank import rerank
from rag.store import Hit, search

Mode = Literal["dense", "lexical", "hybrid", "rerank"]


def retrieve(
    question: str,
    k: int,
    mode: Mode = "rerank",
    collection: chromadb.Collection | None = None,
) -> list[Hit]:
    if mode == "dense":
        return search(question, k=k, collection=collection)
    if mode == "lexical":
        return get_index(collection).search(question, k)
    # Both remaining modes start from a wide, cheap shortlist. `k` is what
    # the caller wants back; CANDIDATE_K is how far down each list we look.

    dense = search(question, k=CANDIDATE_K, collection=collection)
    lexical = get_index(collection).search(question, k=CANDIDATE_K)
    fused = rrf(dense, lexical)

    if mode == "hybrid":
        return fused[:k]
    return rerank(question, fused[:CANDIDATE_K], k=k)
