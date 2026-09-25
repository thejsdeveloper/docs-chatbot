"""Hybrid retrieval, offline. BM25 needs no key; the reranker is faked at the
HTTP boundary so the request we send and the reorder we do are both checked.
"""

import json

import chromadb
import httpx
import pytest

from rag import lexical, rerank
from rag.fusion import rrf
from rag.store import Hit


def hit(source: str, position: int = 0, text: str = "") -> Hit:
    return Hit(text=text or source, source=source, position=position, distance=None)


def test_rrf_promotes_the_hit_both_lists_agree_on():
    dense = [hit("a.md"), hit("b.md"), hit("c.md")]
    bm25 = [hit("c.md"), hit("d.md"), hit("b.md")]

    fused = rrf(dense, bm25)

    # b and c each appear in both lists; a and d in one. Two mid-table
    # appearances beat one first place once k = 60 flattens the curve, which
    # is the point of k.
    assert [h.source for h in fused][:2] == ["c.md", "b.md"]
    assert len(fused) == 4  # deduplicated, nothing lost


def test_lexical_index_finds_exact_identifiers():
    collection = chromadb.EphemeralClient().create_collection("lex-test")
    # Four documents, not two: BM25 weights a word by how rare it is across the
    # corpus, and in a corpus of two everything is half the corpus.
    docs = {
        "x.md": "Call flushSync to force the DOM update.",
        "y.md": "State is a snapshot.",
        "z.md": "Effects run after render.",
        "w.md": "Keys tell React which item is which.",
    }
    collection.add(
        ids=[f"{source}:0" for source in docs],
        embeddings=[[1.0, 0.0]] * len(docs),  # type: ignore[arg-type]
        documents=list(docs.values()),
        metadatas=[{"source": source, "position": 0} for source in docs],
    )

    index = lexical.LexicalIndex(collection)

    assert [h.source for h in index.search("flushSync", k=5)] == ["x.md"]
    assert index.search("nothing here matches", k=5) == []


def test_rerank_reorders_by_the_indices_the_api_returns(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test")
    sent = {}

    def handler(request: httpx.Request) -> httpx.Response:
        sent["body"] = request.read()
        return httpx.Response(
            200,
            json={
                "results": [
                    {"index": 2, "relevance_score": 0.9},
                    {"index": 0, "relevance_score": 0.4},
                ]
            },
        )

    # Route httpx.post through a fake transport; nothing leaves the process.
    client = httpx.Client(transport=httpx.MockTransport(handler))
    monkeypatch.setattr(rerank.httpx, "post", client.post)

    candidates = [hit("a.md"), hit("b.md"), hit("c.md")]
    top = rerank.rerank("q", candidates, k=2)

    assert [h.source for h in top] == ["c.md", "a.md"]
    assert json.loads(sent["body"])["top_n"] == 2


def test_rerank_of_nothing_makes_no_request(monkeypatch):
    monkeypatch.setattr(rerank.httpx, "post", lambda *a, **kw: pytest.fail("called"))
    assert rerank.rerank("q", [], k=4) == []
