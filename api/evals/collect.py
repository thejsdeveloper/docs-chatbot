import json
from pathlib import Path

from evals.llm import complete
from evals.questions import active
from rag.answer import SYSTEM, build_prompt
from rag.store import search

TRACES = Path(__file__).parent / "traces.jsonl"


def run_one(qid: str, question: str) -> dict:
    hits = search(question, k=5)
    answer = complete(SYSTEM, build_prompt(question, [h.text for h in hits]))
    return {
        "id": qid,
        "question": question,
        "answer": answer,
        "sources": [f"{h.source}#{h.position}" for h in hits],
    }


def main() -> None:
    done = set()
    if TRACES.exists():
        done = {
            json.loads(line)["id"]
            for line in TRACES.read_text().splitlines()
            if line.strip()
        }

    with TRACES.open("a") as out:
        for q in active():
            if q.id in done:
                continue
            print(f"{q.id} {q.text}")
            out.write(json.dumps(run_one(q.id, q.text)) + "\n")
            out.flush()


if __name__ == "__main__":
    main()
