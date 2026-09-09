from collections import Counter
from pathlib import Path
from typing import Literal

from jsonschema import ValidationError
from pydantic import BaseModel

ANNOTATIONS = Path(__file__).parent / "annotations.jsonl"

FailureCode = Literal[
    "wrong_answer",
    "unsupported_claim",
    "missed_answer",
    "severed_context",
    "presentation",
]


class Annotation(BaseModel):
    trace_id: str
    verdict: Literal["pass", "fail"]
    note: str
    code: FailureCode | None = None
    grounded: bool | None = None


def load_annotations(path: Path = ANNOTATIONS) -> list[Annotation]:
    lines = path.read_text().splitlines()
    return [Annotation.model_validate_json(line) for line in lines if line.strip()]


def report(annotations: list[Annotation]) -> None:
    total = len(annotations)
    fails = [a for a in annotations if a.verdict == "fail"]
    print(f"{total} traces, {len(fails)} failed ({len(fails) / total:.0%})\n")

    counts = Counter(a.code for a in fails)
    uncoded = counts.pop(None, 0)

    for code, n in counts.most_common():
        bar = "#" * n
        print(f"{n:>3} {code:<18} {bar}")
    if uncoded:
        print(f"\n{uncoded} failures still have no code - run the coding pass.")


if __name__ == "__main__":
    try:
        report(load_annotations())
    except ValidationError as exc:
        print("annotations.jsonl has a bad row:")
        print(exc)
