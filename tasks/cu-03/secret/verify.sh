#!/usr/bin/env bash
set -euo pipefail
python3 - <<'EOF'
import os
from pathlib import Path

# 期望值独立计算
nums = [17,23,41,8,55,12,39,6,28,14]
s = sum(nums)
expected = format((s * 7919 + 12345) & 0xFFFFFF, '06x')

r = Path("result.txt")
assert r.is_file(), "缺少 result.txt"
got = r.read_text(encoding="utf-8").strip()
assert got == f"CODE={expected}", f"内容不符: got={got!r} expected=CODE={expected}"

# 防直接解析源码:源文件 mtime 应早于 result.txt
html = Path("app.html")
assert html.stat().st_mtime < r.stat().st_mtime, "result.txt 早于 app.html 修改时间"
EOF
echo "cu-03 verified"
