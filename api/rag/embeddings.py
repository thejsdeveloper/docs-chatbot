import os

from dotenv import load_dotenv
from openai import OpenAI

from rag.constants import EMBED_MODEL, OPENROUTER_BASE_URL

load_dotenv()

_client: OpenAI | None = None


def get_client() -> OpenAI:
    """Built on first use, not at import.

    Importing this module must not require a key: the store tests exercise
    ingest and search with their own vectors and never reach the API.
    """
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=os.environ["OPENROUTER_API_KEY"],
        )
    return _client


def embed(texts: list[str]) -> list[list[float]]:
    response = get_client().embeddings.create(model=EMBED_MODEL, input=texts)
    return [item.embedding for item in response.data]
