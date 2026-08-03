dev:                       # two processes, one command
	cd api && uv run uvicorn rag.main:app --reload & \
	cd web && npm run dev

fetch:                     # rarely. only when you want newer docs
	cd api && ./scripts/fetch-corpus.sh

ingest:                    # when the corpus changes. costs money
	cd api && uv run python -m rag.ingest corpus

hooks:                     # lint and test what you touched, before it lands
	git config core.hooksPath .githooks
	@echo "pre-commit hook enabled"

setup: fetch ingest hooks  # one command for a fresh clone
	@echo "ready. now run: make dev"

test:                      # both suites. neither needs a key or the network
	cd api && uv run pytest && uv run ruff check . && uv run ruff format --check .
	cd web && npm test