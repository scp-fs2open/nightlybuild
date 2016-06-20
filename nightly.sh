#!/bin/env sh

set -ex

GIT_PATH=$(cat config.yml | shyaml get-value git.repo)
GIT_BRANCH=$(cat config.yml | shyaml get-value git.branch)

echo $GIT_PATH
echo $GIT_BRANCH

PREVIOUS_DIR=$(pwd)

cd "$GIT_PATH"
git checkout "$GIT_BRANCH"

STASHED_CHANGES=false
if ! git diff-index --quiet HEAD --; then
    # Stash changes so we can recover them later
    echo "Stashing local changes for later recovery"
    git stash -u -a
    
    STASHED_CHANGES=true
fi

COMMIT_HASH="$(git rev-parse --short HEAD)"
CURRENT_DATE="$(date +%Y%m%d)"

BUILD_NAME="${CURRENT_DATE}_$COMMIT_HASH"

# Detach HEAD so we don't change the branch we are on
git checkout --detach

# We have a clean working copy, do the changes
echo "dnl Test change" >> configure.ac

TAG_NAME="nightly_$BUILD_NAME"

git add .
git commit -m "Automated nightly commit" --author="Nightly script <nightly@example.com>"
git tag -a "$TAG_NAME" -m "Nightly script tag"
git push --tags

# Go back to the actual branch
git checkout "$GIT_BRANCH"

if [ "$STASHED_CHANGES" = true ]; then
    echo "Restoring previous changes"
    git stash pop
fi
cd "$PREVIOUS_DIR"

# Start monitoring the build
./build_monitor.py "$TAG_NAME"