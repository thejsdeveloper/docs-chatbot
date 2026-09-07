import os

from dotenv import load_dotenv
from openai import OpenAI

from rag.constants import CHAT_MODEL, OPENROUTER_BASE_URL

load_dotenv()

_client: OpenAI | None = None


def get_client() -> OpenAI:
    """Built on first use, not at import, so importing needs no key."""
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=os.environ["OPENROUTER_API_KEY"],
        )
    return _client


def complete(system: str, prompt: str, max_tokens: int = 2000) -> str:
    resp = get_client().responses.create(
        model=CHAT_MODEL,
        max_output_tokens=max_tokens,
        instructions=system,
        input=prompt,
    )

    return resp.output_text
