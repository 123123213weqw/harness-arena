#!/usr/bin/env bash
set -euo pipefail
python3 - <<'EOF'
import json
from pathlib import Path

kept = {}
for line in Path("records.jsonl").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        obj = json.loads(line)
    except Exception:
        continue
    if not isinstance(obj, dict):
        continue
    i, n, s = obj.get("id"), obj.get("name"), obj.get("score")
    if (
        isinstance(i, int) and not isinstance(i, bool)
        and isinstance(n, str) and n
        and isinstance(s, int) and not isinstance(s, bool) and 0 <= s <= 100
    ):
        kept.setdefault(i, {"id": i, "name": n, "score": s})

expected = "".join(
    json.dumps(kept[i], separators=(",", ":"), ensure_ascii=False) + "\n"
    for i in sorted(kept)
)

p = Path("clean.jsonl")
assert p.is_file(), "缺少 clean.jsonl"
got = p.read_text(encoding="utf-8")
assert got == expected, f"不一致:\n--- got ---\n{got}--- expected ---\n{expected}"
EOF
echo "gen-04 verified"
