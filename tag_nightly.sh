#!/bin/env sh

set -ex

GIT_PATH=$1
GIT_BRANCH=$2
TAG_NAME=$3

cd "$GIT_PATH"
git checkout "$GIT_BRANCH"

STASHED_CHANGES=false
if ! git diff-index --quiet HEAD --; then
    # Stash changes so we can recover them later
    echo "Stashing local changes for later recovery"
    git stash -u -a
    
    STASHED_CHANGES=true
fi

# Detach HEAD so we don't change the branch we are on
git checkout --detach

# We have a clean working copy, do the changes
echo "dnl Test change" >> configure.ac

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