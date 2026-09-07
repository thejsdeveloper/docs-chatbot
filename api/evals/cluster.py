from evals.llm import complete
from evals.report import load_annotations

SYSTEM = """You group QA notes into a failure taxonomy. You do not judge quality.

<rules>
- Propose between 4 and 7 categories. No more.
- Every note must fit exactly one category.
- Name each category as a short snake_case code.
- For each category give the code, a one-line definition, and the count.
- If two notes describe the same underlying cause, they share a category even
  if the wording differs.
- Do not invent categories for notes that are not present.
</rules>

Output a plain list. No preamble."""


def main() -> None:
    notes = [a.note for a in load_annotations() if a.verdict == "fail"]
    print(f"clustering {len(notes)} failure notes\n")
    numbered = "\n".join(f"{i}. {note}" for i, note in enumerate(notes, 1))
    print(complete(SYSTEM, f"<notes>\n{numbered}\n</notes>"))


if __name__ == "__main__":
    main()
