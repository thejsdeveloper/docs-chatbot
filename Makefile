dev:                       # two processes, one command
	cd api && uv run uvicorn rag.main:app --reload & \
	cd web && npm run dev

fetch:                     # rarely. only when you want newer docs
	cd api && ./scripts/fetch-corpus.sh

ingest:                    # when the corpus changes. costs money
	cd api && uv run python -m rag.ingest corpus

setup: fetch ingest        # one command for a fresh clone
	@echo "ready. now run: make dev"

test:
	cd api && uv run pytest && uv run ruff check .