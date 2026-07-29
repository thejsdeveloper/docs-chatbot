# docs-chatbot

A RAG chatbot that answers questions about the [Vite](https://vite.dev) documentation.
The docs are fetched from the Vite repo, chunked and embedded into a local Chroma
vector store, and served through a FastAPI endpoint that a Next.js chat UI talks to.

## Layout

```
api/          FastAPI service + ingestion pipeline (Python 3.13, uv)
  rag/        app code — main.py (API), ingest.py (corpus → embeddings)
  scripts/    fetch-corpus.sh — downloads the Vite docs as markdown
  corpus/     fetched markdown (gitignored)
  chroma/     persisted vector store (gitignored)
  tests/
web/          Next.js 16 + React 19 + Tailwind v4 chat UI
Makefile      dev / fetch / ingest / setup / test
```

## Requirements

- Python 3.13 and [uv](https://docs.astral.sh/uv/)
- Node.js 20+
- An OpenAI API key

## Setup

```sh
echo "OPENAI_API_KEY=sk-..." > api/.env
make setup                       # fetch the docs, then embed them
make dev                         # API on :8000, web on :3000
```

`make setup` calls the OpenAI embeddings API, so it costs money. You only need to
re-run it when the corpus changes.

## Commands

| Command | What it does |
| --- | --- |
| `make dev` | Runs the API (uvicorn, reload) and the web dev server together |
| `make fetch` | Re-downloads the Vite docs into `api/corpus/` |
| `make ingest` | Chunks and embeds `api/corpus/` into `api/chroma/` |
| `make setup` | `fetch` + `ingest` — for a fresh clone |
| `make test` | `pytest` and `ruff check` in `api/` |

## Configuration

Environment variables live in `api/.env` (gitignored):

- `OPENAI_API_KEY` — required, used for both embeddings and chat completions

## Status

Scaffolding is in place; the RAG pipeline (`rag/main.py`, `rag/ingest.py`) and the
chat UI in `web/app/page.tsx` are still the starter templates.
