from rag.answer import SYSTEM, build_prompt

REFUSAL = "I don't know based on the documents."


def test_system_prompt_asks_for_the_exact_refusal_string():
    assert REFUSAL in SYSTEM


def test_system_prompt_restricts_the_model_to_the_context():
    assert "ONLY" in SYSTEM
    assert "<context>" in SYSTEM


def test_prompt_fences_the_context_and_keeps_the_question_outside_it():
    prompt = build_prompt("Why does my Effect run twice?", ["chunk one"])
    context = prompt[prompt.index("<context>") : prompt.index("</context>")]

    assert "chunk one" in context
    assert "Why does my Effect run twice?" not in context


def test_every_chunk_survives_and_stays_separated():
    prompt = build_prompt("q", ["first chunk", "second chunk"])

    assert "first chunk" in prompt
    assert "second chunk" in prompt
    assert "---" in prompt, "chunks must not run together into one passage"


def test_no_chunks_still_produces_a_context_block():
    """An empty corpus hit must leave the model with visibly nothing to use --
    that is what triggers the refusal instead of a guess."""
    prompt = build_prompt("q", [])

    assert "<context>\n\n</context>" in prompt
