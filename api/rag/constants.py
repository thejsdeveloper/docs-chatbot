"""Tunables shared across the pipeline.

Only values worth changing from one place live here. Regexes and the component
list in `clean.py` stay put: they are part of that module's logic, not knobs.
"""

# --- OpenRouter -------------------------------------------------------------
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
EMBED_MODEL = "openai/text-embedding-3-small"
CHAT_MODEL = "anthropic/claude-haiku-4.5"
MAX_OUTPUT_TOKENS = 800

# --- Vector store -----------------------------------------------------------
CHROMA_PATH = "./chroma"
COLLECTION_NAME = "docs"
# Embeddings are normalised, so cosine keeps distances in a readable 0-2 range.
DISTANCE_SPACE = "cosine"

# --- Chunking ---------------------------------------------------------------
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
# `####` earns its place: react.dev states its comparisons at h4 ("Fetching
# data with `useEffect`"). Stopping at `###` left those chunks labelled with the
# *other* side of the comparison ("Reading a Promise with `use`"), so the
# breadcrumb mislabelled them rather than merely omitting detail.
HEADERS_TO_SPLIT_ON = [
    ("#", "title"),
    ("##", "section"),
    ("###", "subsection"),
    ("####", "subsubsection"),
]

# --- Retrieval --------------------------------------------------------------
# `search()`'s own default; the API asks for more because the answer prompt has
# room for the extra context.
DEFAULT_K = 3
CHAT_K = 4

# --- Ingestion --------------------------------------------------------------
DEFAULT_CORPUS_DIR = "corpus"

# --- HTTP -------------------------------------------------------------------
CORS_ORIGINS = ["http://localhost:3000"]
