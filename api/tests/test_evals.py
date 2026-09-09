"""The eval suite: every question in the frozen set, checked deterministically.

Runs against traces.jsonl, which `uv run python -m evals.collect` wrote.
It makes no API call, so it is free and fast enough for CI.
"""

import json
from pathlib import Path

import pytest

from evals.checks import CORPUS, run_checks
from evals.questions import active

TRACES = Path(__file__).resolve().parent.parent / "evals" / "traces.jsonl"


def load_traces() -> dict[str, dict]:
    if not TRACES.exists():
        return {}
    rows = (
        json.loads(line) for line in TRACES.read_text().splitlines() if line.strip()
    )
    return {row["id"]: row for row in rows}


TRACES_BY_ID = load_traces()


@pytest.mark.parametrize("q", active(), ids=lambda q: q.id)
def test_answer_passes_checks(q):
    trace = TRACES_BY_ID.get(q.id)
    if trace is None:
        pytest.skip(f"no trace for {q.id}: run uv run python -m evals.collect")
    if not CORPUS.exists():
        pytest.skip("corpus missing: run make fetch")
    failures = run_checks(q, trace)
    assert not failures, "\n".join(f"  {f.check}: {f.detail}" for f in failures)
