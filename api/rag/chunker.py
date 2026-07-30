from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)


def getSections(text: str):
    markdown_header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "title"), ("##", "section"), ("###", "subsection")],
        strip_headers=True,
    )

    return markdown_header_splitter.split_text(text)


def chunk_markdown(text: str, size: int = 400, overlap: int = 50) -> list[str]:
    sections = getSections(text)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=size, chunk_overlap=overlap
    )
    return [_with_heading(doc) for doc in text_splitter.split_documents(sections)]


def _with_heading(doc: Document) -> str:
    """Put the heading INSIDE the text, because embeddings never see metadata"""
    heading = " > ".join(v for v in doc.metadata.values())
    return f"{heading}\n\n{doc.page_content}" if heading else doc.page_content


if __name__ == "__main__":
    path = Path("corpus/releases.md")
    chunks = chunk_markdown(path.read_text())
    for chunk in chunks:
        print(chunk)
        print("-" * 40)
    print(f"{len(chunks)} chunks from {path}")
