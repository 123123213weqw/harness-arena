"""统一供应商配置:四个 harness 共用同一 DeepSeek key / base / model。

这是 Tier-B 对比的前提——模型、任务、工作区保持不变,自由变量只有 harness。
key 解析顺序:环境变量 DEEPSEEK_API_KEY → ~/.config/xharness-bench/credentials.env
(V100 上既有的一千多元余额 key 就存在那里)。
"""
from __future__ import annotations

import os
import re
from pathlib import Path

CRED_FILE = Path.home() / ".config" / "xharness-bench" / "credentials.env"


def _key_from_file() -> str | None:
    try:
        for line in CRED_FILE.read_text(encoding="utf-8").splitlines():
            m = re.match(
                r'\s*(?:export\s+)?DEEPSEEK_API_KEY\s*=\s*["\']?([^\s"\'#]+)', line
            )
            if m:
                return m.group(1)
    except OSError:
        return None
    return None


DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY") or _key_from_file()
DEEPSEEK_BASE = os.environ.get("ARENA_DEEPSEEK_BASE", "https://api.deepseek.com")
# Claude Code 走 DeepSeek 的 Anthropic 兼容端点;codex 走 Responses;xharness/pi 走 chat
DEEPSEEK_ANTHROPIC_BASE = DEEPSEEK_BASE.rstrip("/") + "/anthropic"
DEEPSEEK_MODEL = os.environ.get("ARENA_DEEPSEEK_MODEL", "deepseek-chat")

# 2026-10 DeepSeek 定价(元/百万 token),仅供成本估算,报告标注为估算值
PRICE_CNY_PER_MTOK = {"input": 2.0, "cache_read": 0.4, "output": 8.0}


def estimate_cost_cny(u) -> float:
    """按统一牌价估算成本,用于量级对比,不作为精确账单。

    reasoning 按输出价计(DeepSeek 口径);失败运行的消耗同样计入——
    效率评分惩罚"烧钱没办事"。
    """
    return (
        u.input_tokens / 1e6 * PRICE_CNY_PER_MTOK["input"]
        + u.cache_tokens / 1e6 * PRICE_CNY_PER_MTOK["cache_read"]
        + (u.output_tokens + u.reasoning_tokens) / 1e6 * PRICE_CNY_PER_MTOK["output"]
    )
