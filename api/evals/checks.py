"""Deterministic checks over one collected trace.

No model, no network, no cost. Every function here answers a question that has
one right answer, which is what makes it cheap enough to run on every push.
Anything needing judgement lives in judge.py instead.
"""

from pathlib import Path
from typing import NamedTuple

from evals.questions import Question

REFUSAL = "I don't know based on the documents"
CORPUS = Path(__file__).resolve().parent.parent / "corpus"


class Failure(NamedTuple):
    check: str
    detail: str


def refused(answer: str) -> bool:
    return REFUSAL in answer


def check_refusal(q: Question, trace: dict) -> Failure | None:
    """The corpus either covers the question or it does not, and you decided which."""
    if q.kind == "unanswerable" and not refused(trace["answer"]):
        return Failure("refusal", "answered a question the corpus does not cover")
    if q.kind in ("usage", "ordinary", "multihop") and refused(trace["answer"]):
        return Failure("refusal", "refused a question which corpus cover")
    return None


def check_code_example(q: Question, trace: dict) -> Failure | None:
    """Questions marked needs_code must come back with at least one fenced block."""
    if q.needs_code and "```" not in trace["answer"]:
        return Failure("code_example", "no fenced code block in the answer")
    return None


def check_balanced_fences(q: Question, trace: dict) -> Failure | None:
    """An odd number of ``` means a code block that never closed."""
    if trace["answer"].count("```") % 2:
        return Failure("balanced_fences", "unclosed code fence")
    return None


def check_sources_exist(q: Question, trace: dict) -> Failure | None:
    """Every cited source must name a file that is really in the corpus."""
    missing = [s for s in trace["sources"] if not (CORPUS / s.split("#")[0]).exists()]
    if missing:
        return Failure("sources_exist", f"cited files not in corpus: {missing}")
    return None


CHECKS = [check_refusal, check_code_example, check_balanced_fences, check_sources_exist]


def run_checks(q: Question, trace: dict) -> list[Failure]:
    return [f for check in CHECKS if (f := check(q, trace)) is not None]
