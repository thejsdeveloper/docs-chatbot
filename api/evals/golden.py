"""The golden set for retrieval: questions paired with the pages that answer them.

This is a different artefact from `questions.py`, and the difference is the whole
point. `questions.py` asks "was the answer any good?", which needs a model to run
and a human to judge. This file asks "did the right page come back at all?", which
needs neither. A question belongs here only if you can name the page (or pages)
that must be retrieved for the answer to be possible.

Rules, the same as `questions.py`:

1. `id` is permanent. Never renumber, never reuse.
2. Wording is frozen once a run has been recorded against it.
3. `relevant` holds `source` values exactly as `rag/store.py` writes them: the path
    relative to the corpus root, so "reference/react/use.md", not "use.md".
4. `kind` splits the set into questions whose answer sits on one page, questions
    that compare two things, and questions phrased as a symptom ("why does X
    happen?") where the page that answers them never uses the user's words.
    Reporting the kinds separately is the point of the field.
"""

from typing import Literal, NamedTuple

GoldenKind = Literal["factual", "comparison", "symptom"]


class Golden(NamedTuple):
    id: str
    kind: GoldenKind
    text: str
    relevant: tuple[str, ...]


GOLDEN: list[Golden] = [
    # --- factual (8): the answer lives on one page, and you know which one -----
    Golden(
        "g01",
        "factual",
        "What does the cleanup function returned from useEffect do?",
        ("reference/react/useEffect.md", "learn/synchronizing-with-effects.md"),
    ),
    Golden(
        "g02",
        "factual",
        "How do I update a single field of an object held in state?",
        ("learn/updating-objects-in-state.md",),
    ),
    Golden(
        "g03",
        "factual",
        "How do I add an item to an array in state without mutating it?",
        ("learn/updating-arrays-in-state.md",),
    ),
    Golden(
        "g04",
        "factual",
        "What does useMemo cache, and when does it recompute?",
        ("reference/react/useMemo.md",),
    ),
    Golden(
        "g05",
        "factual",
        "What is a key on a list item for, and what makes a good key?",
        ("learn/rendering-lists.md",),
    ),
    Golden(
        "g06",
        "factual",
        "How does useId produce an id that matches on the server and the client?",
        ("reference/react/useId.md",),
    ),
    Golden(
        "g07",
        "factual",
        "What extra checks does StrictMode turn on in development?",
        ("reference/react/StrictMode.md",),
    ),
    Golden(
        "g08",
        "factual",
        "What does startTransition do to a state update?",
        ("reference/react/startTransition.md",),
    ),
    # --- comparison (8): "why X over Y". The class dense retrieval handles worst,
    # because the words of the question are spread across two pages.
    Golden(
        "g09",
        "comparison",
        "Why use the use hook instead of useEffect to read data?",
        ("reference/react/use.md",),
    ),
    Golden(
        "g10",
        "comparison",
        "What is the difference between useMemo and useCallback?",
        ("reference/react/useCallback.md", "reference/react/useMemo.md"),
    ),
    Golden(
        "g11",
        "comparison",
        "When do I need useLayoutEffect instead of useEffect?",
        ("reference/react/useLayoutEffect.md",),
    ),
    Golden(
        "g12",
        "comparison",
        "When should I move from useState to useReducer?",
        ("learn/extracting-state-logic-into-a-reducer.md",),
    ),
    Golden(
        "g13",
        "comparison",
        "When should I use context instead of passing props down?",
        ("learn/passing-data-deeply-with-context.md",),
    ),
    Golden(
        "g14",
        "comparison",
        "Why does changing a ref not re-render, when changing state does?",
        ("learn/referencing-values-with-refs.md",),
    ),
    Golden(
        "g15",
        "comparison",
        "What is the difference between useDeferredValue and useTransition?",
        ("reference/react/useDeferredValue.md", "reference/react/useTransition.md"),
    ),
    Golden(
        "g16",
        "comparison",
        "When should I wrap a component in memo rather than calling useMemo inside it?",
        ("reference/react/memo.md",),
    ),
    # --- comparison (4 more): questions that came up while building the chat UI.
    Golden(
        "g17",
        "comparison",
        "When appending streamed tokens, why pass an updater function to setState instead of the new value?",
        ("learn/queueing-a-series-of-state-updates.md", "learn/state-as-a-snapshot.md"),
    ),
    Golden(
        "g18",
        "comparison",
        "Should I use useEffectEvent or add the value to the effect's dependency array?",
        (
            "learn/separating-events-from-effects.md",
            "reference/react/useEffectEvent.md",
        ),
    ),
    Golden(
        "g19",
        "comparison",
        "When should I use useSyncExternalStore instead of subscribing in useEffect and copying into state?",
        ("reference/react/useSyncExternalStore.md",),
    ),
    Golden(
        "g20",
        "comparison",
        "Should I keep the scroll position in a ref or in state when scrolling a chat to the bottom?",
        (
            "learn/manipulating-the-dom-with-refs.md",
            "learn/referencing-values-with-refs.md",
        ),
    ),
    # --- symptom (8): the question describes what went wrong on screen, in the
    # words a developer would use before they know the name of the concept. The
    # answering page uses the concept's name and rarely the symptom's. Chosen
    # because the first run missed or nearly missed each of them at k = 4.
    Golden(
        "g21",
        "symptom",
        "Why does a plain variable inside my component reset to zero every time?",
        ("learn/state-a-components-memory.md",),
    ),
    Golden(
        "g22",
        "symptom",
        "When I type quickly, the chat shows an answer for an earlier message. How do I stop that?",
        (
            "learn/synchronizing-with-effects.md",
            "learn/you-might-not-need-an-effect.md",
        ),
    ),
    Golden(
        "g23",
        "symptom",
        "Why does the whole list re-render when I change one item's text?",
        ("reference/react/memo.md",),
    ),
    Golden(
        "g24",
        "symptom",
        "How do I stop the compiler from optimising one particular component?",
        (
            "reference/react-compiler/directives/use-no-memo.md",
            "reference/react-compiler/directives.md",
        ),
    ),
    Golden(
        "g25",
        "symptom",
        "Why does my component render twice when I click once?",
        ("reference/react/StrictMode.md", "learn/keeping-components-pure.md"),
    ),
    Golden(
        "g26",
        "symptom",
        "After I add a message and scroll to the bottom, the scroll lands one message short. Why?",
        ("learn/manipulating-the-dom-with-refs.md", "reference/react-dom/flushSync.md"),
    ),
    Golden(
        "g27",
        "symptom",
        "Why does my accordion forget which panel was open when I toggle a parent boolean?",
        ("learn/preserving-and-resetting-state.md",),
    ),
    Golden(
        "g28",
        "symptom",
        "Why does my modal's typed text survive after I close and reopen it?",
        ("learn/preserving-and-resetting-state.md",),
    ),
]
