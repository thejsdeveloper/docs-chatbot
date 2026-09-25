"""Score the retriever against the golden set. No LLM is involved.

Run from `api/`:

    uv run python -m evals.retrieval                    # dense, k = 4 and k = 20
    uv run python -m evals.retrieval --mode hybrid --k 4

Writes one JSON line per question per k to evals/retrieval-<mode>.jsonl,
overwriting it, so every run is directly comparable to the last run of the
same mode, and the modes can be diffed against each other.
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import get_args

from evals.golden import GOLDEN, Golden
from rag.retrieve import Mode, retrieve
from rag.store import Hit

OUT_DIR = Path(__file__).parent


def first_relevant_rank(hits: list[Hit], relevant: tuple[str, ...]) -> int | None:
    """1-based position of the first hit from a relevant page or None"""
    wanted = set(relevant)

    for rank, hit in enumerate(hits, start=1):
        if hit.source in wanted:
            return rank
    return None


def score_one(golden: Golden, k: int, mode: Mode) -> dict:
    hits = retrieve(golden.text, k=k, mode=mode)
    rank = first_relevant_rank(hits, golden.relevant)
    return {
        "id": golden.id,
        "kind": golden.kind,
        "mode": mode,
        "k": k,
        "rank": rank,
        "recall": 1 if rank else 0,
        "reciprocal_rank": 1 / rank if rank else 0.0,
        "returned": [hit.source for hit in hits[:3]],
    }


def summarise(rows: list[dict]) -> tuple[float, float]:
    """recall@k and MRR over a group of rows. Both are plain averages"""
    if not rows:
        return 0.0, 0.0
    recall = sum(row["recall"] for row in rows) / len(rows)
    mrr = sum(row["reciprocal_rank"] for row in rows) / len(rows)
    return recall, mrr


def main() -> None:
    parser = argparse.ArgumentParser(description="score retrieval on the golden set")
    parser.add_argument("--k", type=int, nargs="+", default=[4, 20])
    parser.add_argument("--mode", choices=get_args(Mode), default="dense")
    args = parser.parse_args()

    all_rows: list[dict] = []
    for k in args.k:
        rows = [score_one(golden, k, args.mode) for golden in GOLDEN]
        all_rows.extend(rows)

        by_kind: dict[str, list[dict]] = defaultdict(list)
        for row in rows:
            by_kind[row["kind"]].append(row)

        recall, mrr = summarise(rows)
        print(f"\nmode = {args.mode}   k = {k}")
        print(
            f"  overall      recall@{k} {recall:.2f}   MRR {mrr:.2f}   (n={len(rows)})"
        )

        for kind in sorted(by_kind):
            kind_recall, kind_mrr = summarise(by_kind[kind])
            n = len(by_kind[kind])
            print(
                f"  {kind:<12} recall@{k} {kind_recall:.2f}   MRR {kind_mrr:.2f}   (n={n})"
            )

        missed = [row["id"] for row in rows if row["rank"] is None]

        if missed:
            print(f"  missed:      {', '.join(missed)}")

    out = OUT_DIR / f"retrieval-{args.mode}.jsonl"
    with out.open("w") as file:
        for row in all_rows:
            file.write(json.dumps(row) + "\n")
    print(f"\nwrote {len(all_rows)} rows to {out}")


if __name__ == "__main__":
    main()
