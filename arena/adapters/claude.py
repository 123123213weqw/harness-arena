"""Claude Code headless 适配,统一走 DeepSeek 的 Anthropic 兼容端点。

已实测(Claude Code 2.1.212):
  ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
  ANTHROPIC_AUTH_TOKEN=<deepseek key>
  ANTHROPIC_MODEL=deepseek-chat
`claude -p --output-format json` 返回 JSON,usage 含
input_tokens/output_tokens/cache_read_input_tokens。
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

from .. import providers
from ..schema import Task
from .base import AgentRun, Usage


class ClaudeCodeAdapter:
    name = "claude-code"
    model = providers.DEEPSEEK_MODEL

    def __init__(self) -> None:
        # ARENA_CLAUDE_BIN 可指定旁路安装的版本(如 ~/claude-287/node_modules/.bin/claude)做版本对照
        override = os.environ.get("ARENA_CLAUDE_BIN")
        self.bin = override if override else shutil.which("claude")

    def run(self, task: Task, workdir: Path) -> AgentRun:
        if not self.bin:
            return AgentRun(ok=False, usage=Usage(), error="未找到 claude CLI,跳过")
        usage = Usage()
        t0 = time.time()
        env = {
            **os.environ,
            "ANTHROPIC_BASE_URL": providers.DEEPSEEK_ANTHROPIC_BASE,
            "ANTHROPIC_AUTH_TOKEN": providers.DEEPSEEK_KEY or "",
            "ANTHROPIC_MODEL": providers.DEEPSEEK_MODEL,
        }
        env.pop("ANTHROPIC_API_KEY", None)
        try:
            r = subprocess.run(
                [
                    self.bin, "-p", task.prompt,
                    "--output-format", "json",
                    "--max-turns", "30",
                    "--dangerously-skip-permissions",
                ],
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=task.timeout_minutes * 60 + 60,
                env=env,
            )
        except subprocess.TimeoutExpired:
            return AgentRun(ok=False, usage=usage, error="claude CLI 超时")
        usage.seconds = time.time() - t0
        arena = workdir / ".arena"
        arena.mkdir(exist_ok=True)
        (arena / "result.json").write_text(r.stdout, encoding="utf-8")
        try:
            data = json.loads(r.stdout)
            u = data.get("usage") or {}
            usage.input_tokens = int(u.get("input_tokens", 0) or 0)
            usage.output_tokens = int(u.get("output_tokens", 0) or 0)
            usage.cache_tokens = int(u.get("cache_read_input_tokens", 0) or 0)
            usage.calls = 1 if usage.input_tokens or usage.output_tokens else 0
        except Exception:
            pass
        return AgentRun(
            ok=r.returncode == 0,
            usage=usage,
            transcript=arena / "result.json",
            error=(r.stderr.strip()[-500:] or None) if r.returncode != 0 else None,
        )
