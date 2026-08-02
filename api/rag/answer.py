SYSTEM = """You answer questions about a set of documents.

Use ONLY the information inside the <context> tags. The context is the
complete set of extracts available to you.

If the context does not contain the answer, reply with exactly:
I don't know based on the documents.

Each chunk begins with its section heading. Use it to orient yourself, but
do not cite it in your answer -- the UI lists the sources separately."""


def build_prompt(question: str, chunks: list[str]) -> str:
    context = "\n\n---\n\n".join(chunks)
    return f"<context>\n{context}\n</context>\n\nQuestion: {question}"
