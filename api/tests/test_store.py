"""Retrieval tests that never touch the network.

Chroma lets callers supply their own vectors, so a fake `embed` turns the
whole ingest/search path into arithmetic we control: no key, no cost, no
flakiness from a model that quietly changes under us.
"""

from uuid import uuid4

import chromadb
import pytest

from rag import store
from rag.chunker import chunk_markdown

# Each document gets a coordinate on the unit circle; cosine distance then
# falls straight out of the angle between them.
VECTORS = {
    "alpha": [1.0, 0.0],
    "beta": [0.0, 1.0],
}


def fake_embed(texts: list[str]) -> list[list[float]]:
    """Vector by keyword: a text is `alpha` if it says so, else `beta`."""
    return [VECTORS["alpha" if "alpha" in t else "beta"] for t in texts]


@pytest.fixture
def collection():
    # chromadb caches the ephemeral client per settings, so the in-memory
    # server outlives the test; a fresh name is what isolates one test's
    # documents from the next.
    return chromadb.EphemeralClient().create_collection(
        f"test-{uuid4().hex}", configuration={"hnsw": {"space": "cosine"}}
    )


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """`store` imported `embed` by value, so patch it in `store`'s namespace."""
    monkeypatch.setattr(store, "embed", fake_embed)


def test_chunks_carry_their_source_and_heading():
    chunks = chunk_markdown("# Install\n\nRun uv sync to install.", size=400)
    assert all("Install" in c for c in chunks)


def test_metadata_filter_never_leaks_across_sources(collection):
    """The query vector is *identical* to document a, so a would win outright
    without the filter. `where` runs before the vector search, which makes a
    not merely outranked but not a candidate -- the assertion does real work."""
    collection.add(
        ids=["a:0", "b:0"],
        embeddings=[VECTORS["alpha"], VECTORS["beta"]],
        documents=["alpha text", "beta text"],
        metadatas=[
            {"source": "a.md", "position": 0},
            {"source": "b.md", "position": 0},
        ],
    )

    hits = store.search("alpha", k=5, where={"source": "b.md"}, collection=collection)

    assert [h.source for h in hits] == ["b.md"]


def test_ingest_ids_are_scoped_to_the_path_not_the_basename(tmp_path, collection):
    """react.dev has nine `index.md` files; on bare basenames the second one
    ingested would silently overwrite the first."""
    for folder in ("learn", "reference"):
        page = tmp_path / folder / "index.md"
        page.parent.mkdir()
        page.write_text(f"# {folder}\n\nalpha text about {folder}.")
        store.ingest(str(page), collection=collection, root=tmp_path)

    assert collection.count() == 2
    assert set(collection.get()["ids"]) == {"learn/index.md:0", "reference/index.md:0"}


def test_ingest_round_trips_source_and_position(tmp_path, collection):
    page = tmp_path / "guide.md"
    page.write_text("# Guide\n\n" + "alpha sentence. " * 200)
    written = store.ingest(str(page), collection=collection, root=tmp_path)

    hits = store.search("alpha", k=written, collection=collection)

    assert written > 1, "corpus needs several chunks for position to mean anything"
    assert {h.source for h in hits} == {"guide.md"}
    assert sorted(h.position for h in hits) == list(range(written))


def test_empty_document_writes_nothing(tmp_path, collection):
    """Chroma rejects an empty `ids` list, so `ingest` has to bail before the
    upsert rather than let the corpus walk blow up on a stub page."""
    page = tmp_path / "empty.md"
    page.write_text("")

    assert store.ingest(str(page), collection=collection, root=tmp_path) == 0
    assert collection.count() == 0


def test_similarity_inverts_distance(collection):
    """The UI ranks on `similarity`; an identical vector must score ~1.0 while
    an orthogonal one lands near 0.0."""
    collection.add(
        ids=["a:0", "b:0"],
        embeddings=[VECTORS["alpha"], VECTORS["beta"]],
        documents=["alpha text", "beta text"],
        metadatas=[
            {"source": "a.md", "position": 0},
            {"source": "b.md", "position": 0},
        ],
    )

    best, worst = store.search("alpha", k=2, collection=collection)

    assert best.source == "a.md"
    assert best.similarity == pytest.approx(1.0, abs=1e-6)
    assert worst.similarity == pytest.approx(0.0, abs=1e-6)
