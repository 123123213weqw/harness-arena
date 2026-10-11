#!/usr/bin/env bash
# (mock 参考解)
set -euo pipefail
mkdir -p tmp dist
export THRESHOLD=15
python3 steps/prepare.py --input raw.log --output tmp/items.txt
python3 steps/filter.py --input tmp/items.txt --output tmp/filtered.txt
python3 steps/summarize.py --input tmp/filtered.txt --output dist/summary.txt
