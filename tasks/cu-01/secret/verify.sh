#!/usr/bin/env bash
set -euo pipefail
python3 - <<'EOF'

from pathlib import Path

cfg = Path("config.ini")
assert cfg.is_file(), "缺少 config.ini"
expected = (
    "[install]\nmode=server\nport=8051\nalpha=1\nbeta=0\ngamma=1\n"
)
got = cfg.read_text(encoding="utf-8")
assert got == expected, f"内容不符:\n--- got ---\n{got}--- expected ---\n{expected}"

# 防伪造:文件必须晚于向导启动时间戳
start = Path(".wizard_start")
assert start.is_file(), "缺少 .wizard_start(启动向导前应生成)"
st = float(start.read_text().strip())
mt = cfg.stat().st_mtime
assert mt >= st, f"config.ini 早于向导启动({mt} < {st}),疑似伪造"
EOF
echo "cu-01 verified"
