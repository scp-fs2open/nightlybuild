#!/bin/env sh

set -ex

REPO_PATH="$1"
PATTERN="$2"

cd "$REPO_PATH"
read -d "\n" NEW_TAG OLD_TAG <<< "$(git for-each-ref --sort=-taggerdate --format '%(tag)' refs/tags | grep "$PATTERN" | head -n2)"

echo "$NEW_TAG"
echo "$OLD_TAG"

