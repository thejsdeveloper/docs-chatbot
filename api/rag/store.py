from pathlib import Path
from typing import cast

import chromadb
from chromadb.api.types import Embeddings
from pydantic import BaseModel

from rag.chunker import chunk_markdown
from rag.constants import (
    CHROMA_PATH,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    DEFAULT_K,
    DISTANCE_SPACE,
)
from rag.embeddings import embed

_client = None


class Hit(BaseModel):
    text: str
    source: str
    position: int
    distance: float

    @property
    def similarity(self) -> float:
        return 1.0 - self.distance


def get_collection() -> chromadb.Collection:
    """Open (once) and return the collection. Called from lifespan"""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
    return _client.get_or_create_collection(
        COLLECTION_NAME, configuration={"hnsw": {"space": DISTANCE_SPACE}}
    )


def ingest(
    path: str,
    size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
    collection: chromadb.Collection | None = None,
    root: str | Path | None = None,
) -> int:
    """Ingest one file. Returns the number of chunks written.

    `source` is the path relative to the corpus root, not the bare filename:
    react.dev has nine `index.md` files plus five other duplicated basenames,
    which would collide on id and silently overwrite each other.
    """
    collection = collection or get_collection()
    source = str(Path(path).relative_to(root)) if root else Path(path).name
    chunks = chunk_markdown(Path(path).read_text(), size, overlap)
    if not chunks:
        return 0
    collection.upsert(
        ids=[f"{source}:{i}" for i in range(len(chunks))],
        embeddings=cast(Embeddings, embed(chunks)),
        documents=chunks,
        metadatas=[{"source": source, "position": i} for i in range(len(chunks))],
    )
    print(f"ingested {len(chunks)} chunks from {source}")
    return len(chunks)


def search(
    question: str,
    k: int = DEFAULT_K,
    where: dict | None = None,
    collection: chromadb.Collection | None = None,
) -> list[Hit]:
    collection = collection or get_collection()
    results = collection.query(
        query_embeddings=cast(Embeddings, embed([question])),
        n_results=k,
        where=where,
    )

    documents = results["documents"]
    metadatas = results["metadatas"]
    distances = results["distances"]

    assert documents is not None and metadatas is not None and distances is not None

    return [
        Hit(
            text=doc,
            distance=dist,
            source=str(meta["source"]),
            position=int(meta["position"]),  # type: ignore[arg-type]
        )
        for doc, meta, dist in zip(documents[0], metadatas[0], distances[0])
    ]
