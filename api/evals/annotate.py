import json
import sys
from pathlib import Path
from typing import get_args

from evals.report import ANNOTATIONS, Annotation, FailureCode, load_annotations

TRACES = Path(__file__).parent / "traces.jsonl"
CODES = list(get_args(FailureCode))


def load_traces() -> list[dict]:
    lines = TRACES.read_text().splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def already_done() -> set[str]:
    if not ANNOTATIONS.exists():
        return set()
    return {a.trace_id for a in load_annotations()}


def open_pass() -> None:
    done = already_done()
    traces = [t for t in load_traces() if t["id"] not in done]
    print(f"{len(traces)} traces left to read. \n")

    with ANNOTATIONS.open("a") as out:
        for i, trace in enumerate(traces, 1):
            print("=" * 70)
            print(f"[{i} / {len(traces)}]  {trace['id']}")
            print(f"\nQ: {trace['question']}\n")
            print(f"A: {trace['answer']}\n")
            print("sources: " + ", ".join(trace["sources"]))
            print("-" * 70)

            verdict = ""
            while verdict not in ("p", "f"):
                verdict = input("pass or fail ? [p/f] (q to stop) : ").strip().lower()
                if verdict == "q":
                    return

            note = input("what went wrong or right ? ").strip()

            row = Annotation(
                trace_id=trace["id"],
                verdict="pass" if verdict == "p" else "fail",
                note=note,
            )

            out.write(row.model_dump_json() + "\n")
            out.flush()
            print()


def coding_pass() -> None:
    rows = load_annotations()
    for i, code in enumerate(CODES):
        print(f" {i} {code}")
    print()

    for row in rows:
        if row.verdict == "fail" and row.code is None:
            print(f"\n{row.trace_id}: {row.note}")
            choice = input(f"code [0-{len(CODES) - 1}]: ").strip()
            if choice.isdigit() and int(choice) < len(CODES):
                row.code = CODES[int(choice)]

    ANNOTATIONS.write_text("".join(r.model_dump_json() + "\n" for r in rows))


def grounded_pass() -> None:
    """Label the one property the judge will be built for, and nothing else."""
    traces = {t["id"]: t for t in load_traces()}
    rows = load_annotations()

    for row in rows:
        if row.grounded is not None:
            continue
        trace = traces[row.trace_id]
        print("=" * 70)
        print(f"{row.trace_id}\n\nQ: {trace['question']}\n")
        print("CONTEXT THE MODEL WAS GIVEN:\n")
        for chunk in trace.get("chunks", []):
            print(chunk[:600] + "\n" + "-" * 30)
        print(f"\nA: {trace['answer']}\n")
        print("Is every claim in the answer supported by the context above?")

        answer = ""
        while answer not in ("y", "n"):
            answer = input("grounded ? [y/n] (q to stop) : ").strip().lower()
            if answer == "q":
                break
        if answer == "q":
            break
        row.grounded = answer == "y"

    ANNOTATIONS.write_text("".join(r.model_dump_json() + "\n" for r in rows))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "open"
    if mode == "open":
        open_pass()
    elif mode == "code":
        coding_pass()
    elif mode == "ground":
        grounded_pass()
    else:
        print("usage: uv run  python -m evals.annotate [open|code]")
