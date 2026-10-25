#!/usr/bin/env bash
# 第九轮起的标准跑法:全上游 2026-10-25 版 + 思考全开
#   xharness 9c9dabe | claude-code 2.1.310 | codex 0.164.0 | pi 1.4.0 (Node 22.20)
# 用法: bash scripts/run-thinking.sh [额外 arena 参数...]
set -euo pipefail
cd "$(dirname "$0")/.."

export PATH="$HOME/node22/bin:$PATH"          # pi 1.4+/codex 0.164 需要 Node >= 22
export ARENA_DEEPSEEK_MODEL=deepseek-flash
export XHARNESS_PROTOCOL=responses
export XHARNESS_MAX_OUTPUT=65536              # 默认 12288 会被思考烧光(第七轮教训)
export ARENA_CODEX_REASONING=high
export MAX_THINKING_TOKENS=32000
export ARENA_PI_THINKING=high
export ARENA_CLAUDE_BIN="$HOME/claude-latest/node_modules/.bin/claude"  # 2.1.310 旁路安装,不动 qqbot 的 2.1.212

exec bash -lc ".venv/bin/python -m arena --adapters xharness,claude-code,codex,pi --repeats 2 $*"
