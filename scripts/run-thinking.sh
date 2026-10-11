#!/usr/bin/env bash
# 第四轮起的标准跑法:统一模型 deepseek-flash + 四臂思考全开
# 用法: bash scripts/run-thinking.sh [额外 arena 参数...]
set -euo pipefail
cd "$(dirname "$0")/.."

export ARENA_DEEPSEEK_MODEL=deepseek-flash   # DeepSeek 2026 真实模型名(1M 上下文,effort low/high/max)
export XHARNESS_PROTOCOL=responses            # xharness 切 Responses 协议 → 服务端默认 effort=high(reasoning 独立计账)
export ARENA_CODEX_REASONING=high             # codex 显式 effort=high
export MAX_THINKING_TOKENS=32000              # claude 思考预算:不设人为上限,放到模型输出上限(第四轮 8000 曾把 hard-03 掐死在半路)
export ARENA_PI_THINKING=high                 # pi --thinking high(chat 内联思考)

exec bash -lc ".venv/bin/python -m arena --adapters xharness,claude-code,codex,pi --repeats 2 $*"
