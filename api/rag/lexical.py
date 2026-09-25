"""BM25 over the same chunks the vector store holds. No embeddings, no key.

The index is built in memory from `collection.get()`, so it always describes
exactly the chunks the dense search sees. Rebuilding it after an ingest is
therefore free: restart the process and it comes back in step.
"""

import re

import chromadb
from rank_bm25 import BM25Okapi

from rag.store import Hit, get_collection

# Lower-case words and numbers, nothing else. `useEffect` becomes `useeffect`,
# so the query "useEffect" and a chunk that says `useEffect(` match.
_TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


class LexicalIndex:
    def __init__(self, collection: chromadb.Collection):
        got = collection.get(include=["documents", "metadatas"])
        self.documents = got["documents"] or []
        self.metadatas = got["metadatas"] or []
        self._bm25 = BM25Okapi([tokenize(doc) for doc in self.documents])

    def search(self, question: str, k: int) -> list[Hit]:
        scores = self._bm25.get_scores(tokenize(question))
        top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [
            Hit(
                text=self.documents[i],
                source=str(self.metadatas[i]["source"]),
                position=int(self.metadatas[i]["position"]),  # type: ignore[arg-type]
                distance=None,
            )
            for i in top
            if scores[i] > 0
        ]


_index: LexicalIndex | None = None


def get_index(collection: chromadb.Collection | None = None) -> LexicalIndex:
    """Built on first use, once per process. Same shape as `store.get_collection`."""
    global _index
    if _index is None:
        _index = LexicalIndex(collection or get_collection())
    return _index
