#!/usr/bin/env bash
set -euo pipefail
python3 - <<'EOF'
from pathlib import Path

led = Path("ledger.txt")
assert led.is_file(), "缺少 ledger.txt"
got = led.read_text(encoding="utf-8")
assert got == "arena:835\n", f"内容不符: {got!r}"

start = Path(".cu_start")
assert start.is_file(), "缺少 .cu_start 时间戳"
assert led.stat().st_mtime >= float(start.read_text().strip()), "ledger.txt 早于启动时间戳,疑似伪造"
EOF
echo "cu-02 verified"
