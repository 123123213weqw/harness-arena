#!/usr/bin/env bash
set -euo pipefail
rm -rf tmp dist
bash pipeline.sh >/dev/null 2>&1 || { echo "pipeline.sh 执行失败"; exit 1; }

python3 - <<'EOF'
from pathlib import Path

values = []
for line in Path("raw.log").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line:
        continue
    _name, _, v = line.partition(",")
    values.append(int(v.strip()))

kept = [v for v in values if v >= 15]
dropped = len(values) - len(kept)
s = sum(kept)
avg = f"{s / len(kept):.2f}" if kept else "0.00"
expected = f"sum={s}\nkept={len(kept)}\ndropped={dropped}\navg={avg}\n"

got = Path("dist/summary.txt").read_text(encoding="utf-8")
assert got == expected, f"不一致:\n--- got ---\n{got}--- expected ---\n{expected}"
EOF
echo "ops-02 verified"
