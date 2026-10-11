#!/usr/bin/env bash
# 统计 data.tsv 的非空行数,经 counter.py 写入 dist/output.txt(mock 参考解)
set -euo pipefail
mkdir -p dist
python3 counter.py --input data.tsv --output dist/output.txt
