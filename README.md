# react-docs-chatbot

A RAG chatbot that answers questions about the [React](https://react.dev) documentation.
The docs are fetched from the [react.dev](https://github.com/reactjs/react.dev) repo,
cleaned, chunked and embedded into a local Chroma vector store, and served through a
FastAPI endpoint that a Next.js chat UI talks to.

## Layout

```
api/          FastAPI service + ingestion pipeline (Python 3.13, uv)
  rag/        app code
    main.py     API — /health and the /chat/stream SSE endpoint
    ingest.py   corpus → embeddings
    clean.py    react.dev MDX → plain markdown
    chunker.py  header-aware splitting
    store.py    Chroma collection, ingest + search
  scripts/    fetch-corpus.sh — downloads react.dev's src/content
  corpus/     fetched markdown (gitignored)
  chroma/     persisted vector store (gitignored)
  tests/
web/          Next.js 16 + React 19 + Tailwind v4 chat UI
Makefile      dev / fetch / ingest / setup / test
```

## Requirements

- Python 3.13 and [uv](https://docs.astral.sh/uv/)
- Node.js 20+
- An [OpenRouter](https://openrouter.ai) API key

## Setup

```sh
echo "OPENROUTER_API_KEY=sk-or-..." > api/.env
make setup                       # fetch the docs, then embed them
make dev                         # API on :8000, web on :3000
```

`make setup` calls an embeddings API, so it costs money — about 1.5 cents for the
full corpus. You only need to re-run it when the corpus or the cleaning changes.

## Commands

| Command | What it does |
| --- | --- |
| `make dev` | Runs the API (uvicorn, reload) and the web dev server together |
| `make fetch` | Re-downloads react.dev's docs into `api/corpus/` |
| `make ingest` | Cleans, chunks and embeds `api/corpus/` into `api/chroma/` |
| `make setup` | `fetch` + `ingest` — for a fresh clone |
| `make test` | `pytest` and `ruff check` in `api/` |

## Configuration

Environment variables live in `api/.env` (gitignored):

- `OPENROUTER_API_KEY` — required, used for both embeddings and chat completions

Models are set in code: `openai/text-embedding-3-small` for embeddings
(`rag/embeddings.py`) and `anthropic/claude-haiku-4.5` for answers (`rag/main.py`).

## Notes on the corpus

react.dev is MDX rather than plain markdown, so `rag/clean.py` normalises it before
chunking. Three things it handles that matter for retrieval:

- **Titles live in frontmatter, not `#` headings.** Only 2 of 222 files have an h1, so
  the title is promoted into one — otherwise chunks lose the word the question is
  usually about.
- **Doc-site components are stripped, code is not.** 297 distinct capitalised tags
  appear *inside* code fences as React examples; only a closed list of chrome
  components (`<Note>`, `<Sandpack>`, …) is removed, and only outside fences.
- **Relative links are stripped.** `[useState](/reference/react/useState)` resolves
  against react.dev, not against this app, so the label is kept and the target
  dropped. Attribution comes from the sources list instead, which is built from
  stored metadata rather than generated text.
