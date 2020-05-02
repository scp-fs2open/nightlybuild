#!/bin/bash

cd "$(dirname "$0")"
exec ./py-env/bin/python nightly.py > nightly.log 2>&1
