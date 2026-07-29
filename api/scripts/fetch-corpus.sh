#!/usr/bin/env bash
set -euo pipefail
mkdir -p corpus && cd corpus
curl -sL https://codeload.github.com/vitejs/vite/tar.gz/refs/heads/main \
  | tar -xz --strip-components=2 "vite-main/docs"
find . -type f ! -name "*.md" -delete
find . -type d -empty -delete
echo "fetched $(find . -name '*.md' | wc -l) markdown files"