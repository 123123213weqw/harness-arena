#!/usr/bin/env bash
# 统计 data.txt 的非空行数,经 counter.py 写入 dist/output.txt
set -euo pipefail
python3 counter.py --input data.txt --output dist/output.txt
