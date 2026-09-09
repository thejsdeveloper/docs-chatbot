"""Does the judge agree with you? Report TPR and TNR, never raw agreement.

The positive class is "ungrounded", because that is what we want to detect.
"""

import json
from pathlib import Path

from evals.report import load_annotations

JUDGEMENTS = Path(__file__).parent / "judgements.jsonl"


def load_judgements(path: Path = JUDGEMENTS) -> dict[str, str]:
    lines = path.read_text().splitlines()
    rows = (json.loads(line) for line in lines if line.strip())
    return {r["trace_id"]: r["verdict"] for r in rows}


def main() -> None:
    judged = load_judgements()
    human = {
        a.trace_id: a.grounded
        for a in load_annotations()
        if a.grounded is not None and a.trace_id in judged
    }
    if not human:
        print("no labelled traces: run uv run python -m evals.annotate ground")
        return

    true_positives = [t for t, g in human.items() if not g and judged[t] == "fail"]
    false_negatives = [t for t, g in human.items() if not g and judged[t] == "pass"]
    true_negatives = [t for t, g in human.items() if g and judged[t] == "pass"]
    false_positives = [t for t, g in human.items() if g and judged[t] == "fail"]

    positives = len(true_positives) + len(false_negatives)
    negatives = len(true_negatives) + len(false_positives)

    print(
        f"{len(human)} labelled traces: {positives} ungrounded, {negatives} grounded\n"
    )
    print(f"{'':<20}{'judge: fail':>11}{'judge: pass':>14}")
    print(
        f"{'actual: ungrounded':<20}{len(true_positives):>11}{len(false_negatives):>14}"
    )
    print(
        f"{'actual: grounded':<20}{len(false_positives):>11}{len(true_negatives):>14}\n"
    )
    if positives:
        print(f"TPR (recall on ungrounded)  : {len(true_positives) / positives:.0%}")
    if negatives:
        print(f"TNR (specificity on grounded): {len(true_negatives) / negatives:.0%}")
    if false_negatives:
        print(f"\nfalse negatives: {', '.join(sorted(false_negatives))}")
    if false_positives:
        print(f"false positives: {', '.join(sorted(false_positives))}")
    print("\nRead the critiques on every disagreement before touching the prompt.")


if __name__ == "__main__":
    main()
