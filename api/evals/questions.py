"""The frozen eval question set for the react.dev docs chatbot.

Rules for this file:

1. `id` is permanent. Never renumber, never reuse. Annotations from every
    past run are keyed on it.
2. Wording is frozen. Editing a question makes this week's run
    incomparable to last week's, which is the whole reason the set exists.
3. To retire a question, leave the row and set `retired=True`. To add one,
    append with the next free id. The set only ever grows.

`kind` is not used by the collector. It exists so the report can tell you
"you pass 9/10 ordinary questions but 1/4 multi-hop", which is a far more
useful sentence than "you scored 22/30".
"""

from typing import Literal, NamedTuple

Kind = Literal["usage", "ordinary", "multihop", "unanswerable", "ambiguous"]


class Question(NamedTuple):
    id: str
    kind: Kind
    text: str
    retired: bool = False


QUESTIONS: list[Question] = [
    # --- usage (10): things actually asked while building and using the app
    Question(
        "q01", "usage", "What does the cleanup function returned from useEffect do?"
    ),
    Question("q02", "usage", "When does React re-run an effect?"),
    Question("q03", "usage", "Why does my effect run twice in development?"),
    Question(
        "q04", "usage", "How do I update a single field of an object held in state?"
    ),
    Question(
        "q05", "usage", "How do I add an item to an array in state without mutating it?"
    ),
    Question(
        "q06",
        "usage",
        "Why is my state still the old value right after I call the setter?",
    ),
    Question(
        "q07",
        "usage",
        "When should I use a key on a list item, and what makes a good key?",
    ),
    Question(
        "q08",
        "usage",
        "How do I pass a value deep down the tree without prop drilling?",
    ),
    Question("q09", "usage", "How do I focus an input imperatively from React?"),
    Question("q10", "usage", "What are the rules of hooks?"),
    # --- ordinary (10): the everyday path a React dev walks
    Question("q11", "ordinary", "What is the difference between props and state?"),
    Question("q12", "ordinary", "How do I render something conditionally in JSX?"),
    Question(
        "q13", "ordinary", "Why do I need curly braces to use JavaScript inside JSX?"
    ),
    Question("q14", "ordinary", "What does it mean for a component to be pure?"),
    Question("q15", "ordinary", "How do I share state between two sibling components?"),
    Question("q16", "ordinary", "When should I use useReducer instead of useState?"),
    Question("q17", "ordinary", "How do I write a custom hook?"),
    Question(
        "q18",
        "ordinary",
        "What is the difference between the render phase and the commit phase?",
    ),
    Question("q19", "ordinary", "How do I type component props in TypeScript?"),
    Question("q20", "ordinary", "What does the 'use client' directive do?"),
    # --- multihop (4): the answer genuinely lives on two different pages
    Question(
        "q21",
        "multihop",
        "How do refs differ from state, and why does changing a ref not re-render "
        "the component?",
    ),
    Question(
        "q22",
        "multihop",
        "I am fetching data in useEffect. When is that the wrong tool, and what "
        "should I use instead?",
    ),
    Question(
        "q23",
        "multihop",
        "How does React decide whether to preserve or reset a component's state "
        "when the tree changes, and how does that relate to keys?",
    ),
    Question(
        "q24",
        "multihop",
        "What is the difference between an event handler and an effect, and how "
        "do I read the latest prop inside an effect without re-running it?",
    ),
    # --- unanswerable (3): the corpus genuinely does not cover these
    Question(
        "q25", "unanswerable", "How do I animate a list reorder with Framer Motion?"
    ),
    Question(
        "q26",
        "unanswerable",
        "How do I deploy a React app to AWS Lambda behind CloudFront?",
    ),
    Question(
        "q27",
        "unanswerable",
        "What is the default revalidation TTL for a fetch in the Next.js App Router?",
    ),
    # --- ambiguous (3): real users type like this
    Question("q28", "ambiguous", "hooks not working"),
    Question("q29", "ambiguous", "why my state not updating??"),
    Question(
        "q30",
        "ambiguous",
        "how to use react context vs redux which is better for my app",
    ),
]


def active() -> list[Question]:
    return [q for q in QUESTIONS if not q.retired]
