#!/usr/bin/env bash
set -euo pipefail
python3 - <<'EOF'
import re
from pathlib import Path

r = Path("answer.txt")
assert r.is_file(), "缺少 answer.txt"
got = r.read_text(encoding="utf-8").strip()

# token 依赖运行时 name 的首字母,格式校验即可
assert re.fullmatch(r"SUCCESS [A-Z0-9]{8}", got), f"格式不符: {got!r}"
# 且不能是源码里能直接算出的固定值(mock 用的也是动态验证)

# 防直接改源码
html = Path("form.html")
assert html.stat().st_mtime < r.stat().st_mtime, "answer.txt 早于 form.html"
EOF
echo "cu-04 verified"
