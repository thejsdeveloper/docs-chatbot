from pathlib import Path
from typing import cast

import chromadb
from chromadb.api.types import Embeddings
from pydantic import BaseModel

from rag.chunker import chunk_markdown
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
        _client = chromadb.PersistentClient(path="./chroma")
    return _client.get_or_create_collection(
        "docs", configuration={"hnsw": {"space": "cosine"}}
    )


def ingest(
    path: str,
    size: int = 400,
    overlap: int = 50,
    collection: chromadb.Collection | None = None,
) -> int:
    collection = collection or get_collection()
    source = Path(path).name
    chunks = chunk_markdown(Path(path).read_text(), size, overlap)
    collection.upsert(
        ids=[f"{source}:{i}" for i in range(len(chunks))],
        embeddings=cast(Embeddings, embed(chunks)),
        documents=chunks,
        metadatas=[{"source": source, "position": i} for i in range(len(chunks))],
    )
    print(f"ingested {len(chunks)} chunks from {source}")
    return collection.count()


def search(
    question: str,
    k: int = 3,
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
