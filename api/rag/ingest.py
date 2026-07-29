import sys
from pathlib import Path

from rag.store import ingest

if __name__ == "__main__":
    folder = Path(sys.argv[1] if len(sys.argv) > 1 else "corpus")
    total = 0
    for path in sorted(folder.rglob("*.md")):
        total += ingest(str(path))
    print(f"ingested {total} chunks from {folder}")
