#!/usr/bin/env bash
set -euo pipefail
python3 - <<'EOF'
from pathlib import Path

rows = set()
for line in Path("events.csv").read_text(encoding="utf-8").splitlines()[1:]:
    line = line.strip()
    if not line:
        continue
    parts = line.split(",")
    if len(parts) != 3:
        continue
    user, _event, minutes = (p.strip() for p in parts)
    if not minutes.lstrip("-").isdigit():
        continue
    m = int(minutes)
    if m < 0:
        continue
    rows.add((user.lower(), _event, m))

totals = {}
for user, _event, m in rows:
    totals[user] = totals.get(user, 0) + m
expected = ["user,total"] + [
    f"{u},{t}" for u, t in sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))
]

p = Path("summary.csv")
assert p.is_file(), "缺少 summary.csv"
got = [l for l in p.read_text(encoding="utf-8").strip().splitlines() if l.strip()]
assert got == expected, f"不一致:\n--- got ---\n" + "\n".join(got) + "\n--- expected ---\n" + "\n".join(expected)
EOF
echo "data-02 verified"
