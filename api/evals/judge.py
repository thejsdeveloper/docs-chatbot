"""One judge, one failure mode: is the answer grounded in the retrieved chunks?

Not "is this a good answer". A judge with a broad remit gives you a number you
cannot act on. This one asks a single question a reader could also answer from
the trace alone, which is what makes it possible to check the judge.
"""

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from evals.llm import get_client

TRACES = Path(__file__).parent / "traces.jsonl"
JUDGEMENTS = Path(__file__).parent / "judgements.jsonl"

MODEL = "anthropic/claude-haiku-4.5"


class Judgement(BaseModel):
    critique: str
    verdict: Literal["pass", "fail"]


JUDGE_SYSTEM = """You are grading one answer produced by a documentation
assistant. You are grading exactly one property and nothing else:

GROUNDEDNESS: every factual claim in the answer must be supported by the
extracts in <context>. An answer is grounded even if it is incomplete, badly
written, or missing a code example. An answer is NOT grounded if it states
anything the extracts do not support, however true that thing is in general.

The refusal "I don't know based on the documents." is always grounded.

First write a critique naming the specific claims you checked and where in the
context you found them, or did not. Then give the verdict.

<example>
<context>useState returns a pair: the current state and a setter.</context>
<answer>useState returns the current state and a setter. It is faster than
useReducer.</answer>
<critique>The first sentence is supported by the extract. The performance
comparison with useReducer appears nowhere in the context.</critique>
<verdict>fail</verdict>
</example>"""


def judge_one(trace: dict) -> Judgement:
    context = "\n\n---\n\n".join(trace["chunks"])
    resp = get_client().chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM},
            {
                "role": "user",
                "content": (
                    f"<context>\n{context}\n</context>\n\n"
                    f"<question>{trace['question']}</question>\n\n"
                    f"<answer>{trace['answer']}</answer>"
                ),
            },
        ],
        response_format=Judgement,
    )
    message = resp.choices[0].message
    if message.parsed is None:
        raise RuntimeError(
            f"judge returned no parsable judgement (refusal: {message.refusal!r})"
        )
    return message.parsed


def main() -> None:
    done = set()
    if JUDGEMENTS.exists():
        done = {
            json.loads(line)["trace_id"]
            for line in JUDGEMENTS.read_text().splitlines()
            if line.strip()
        }

    traces = [
        json.loads(line) for line in TRACES.read_text().splitlines() if line.strip()
    ]
    with JUDGEMENTS.open("a") as out:
        for t in traces:
            if t["id"] in done:
                continue
            judgement = judge_one(t)
            out.write(
                json.dumps({"trace_id": t["id"], **judgement.model_dump()}) + "\n"
            )
            out.flush()
            print(f"{t['id']}  {judgement.verdict}")


if __name__ == "__main__":
    main()
