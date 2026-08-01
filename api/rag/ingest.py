import sys
from pathlib import Path

from rag.store import get_collection, ingest

if __name__ == "__main__":
    folder = Path(sys.argv[1] if len(sys.argv) > 1 else "corpus")
    collection = get_collection()
    total = 0
    for path in sorted(folder.rglob("*.md")):
        total += ingest(str(path), collection=collection, root=folder)
    print(f"ingested {total} chunks from {folder} ({collection.count()} in collection)")
