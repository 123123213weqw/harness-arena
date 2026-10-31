#!/usr/bin/env bash
set -euo pipefail
python3 - <<'EOF'
from pathlib import Path

exp = Path("secret/expected.csv").read_text(encoding="utf-8").strip()
p = Path("cleaned.csv")
assert p.is_file(), "缺少 cleaned.csv"
got = p.read_text(encoding="utf-8").strip()
assert got == exp, f"内容不一致:\n--- got ---\n{got}\n--- expected ---\n{exp}"
EOF
echo "data-01 verified"
