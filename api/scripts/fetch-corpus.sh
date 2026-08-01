#!/usr/bin/env bash
set -euo pipefail
mkdir -p corpus && cd corpus
curl -sL https://codeload.github.com/reactjs/react.dev/tar.gz/refs/heads/main \
  | tar -xz --strip-components=3 "react.dev-main/src/content"
# community/ is team bios and meetup listings; errors/ is three copies of the
# same "minified error" boilerplate. Neither is reference material.
rm -rf community errors
find . -type f ! -name "*.md" -delete
find . -type d -empty -delete
echo "fetched $(find . -name '*.md' | wc -l) markdown files"
