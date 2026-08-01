import os
from collections.abc import AsyncIterable
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.sse import EventSourceResponse, ServerSentEvent
from openai import AsyncOpenAI
from pydantic import BaseModel

from rag.answer import SYSTEM, build_prompt
from rag.store import get_collection, search

MODEL = "anthropic/claude-haiku-4.5"
resources: dict = {}
llm = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    resources["collection"] = get_collection()
    print(f"ready: {resources['collection'].count()} chunks")
    yield
    resources.clear()


app = FastAPI(title="Docs Chatbot", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Ask(BaseModel):
    question: str
    k: int = 4


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "chunks": resources["collection"].count()}


@app.post("/chat/stream", response_class=EventSourceResponse)
async def chat_stream(req: Ask) -> AsyncIterable[ServerSentEvent]:
    hits = search(question=req.question, k=req.k, collection=resources["collection"])
    yield ServerSentEvent(data=[h.model_dump() for h in hits], event="sources")
    prompt = build_prompt(req.question, [h.text for h in hits])

    try:
        async with llm.responses.stream(
            model=MODEL, max_output_tokens=800, instructions=SYSTEM, input=prompt
        ) as stream:
            async for event in stream:
                if event.type == "response.output_text.delta":
                    yield ServerSentEvent(data=event.delta, event="token")
    # Deliberate catch-all: this is the stream boundary. Anything that escapes
    # here truncates the SSE response with no error event, so the client would
    # just see the stream stop. Log the real thing, show a safe thing.
    except Exception as exc:  # noqa: BLE001
        print(f"stream failed: {exc!r}")
        yield ServerSentEvent(data="Sorry, the answer stream failed.", event="error")

    yield ServerSentEvent(raw_data="[DONE]", event="done")
