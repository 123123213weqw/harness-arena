"""Codex CLI headless 适配,统一走 DeepSeek 的 Responses API。

已实测(codex-cli 0.142.0):wire_api 只剩 "responses",DeepSeek 原生支持
/responses 端点,可直连。~/.codex/config.toml 需有:

  [model_providers.deepseek]
  name = "DeepSeek"
  base_url = "https://api.deepseek.com/v1"
  env_key = "DEEPSEEK_API_KEY"
  wire_api = "responses"

`codex exec --json` 输出 jsonl 事件;token_count 事件的
info.total_token_usage 为累计口径,取最后一个即全程用量。
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


class CodexAdapter:
    name = "codex"
    model = providers.DEEPSEEK_MODEL

    def __init__(self) -> None:
        self.bin = shutil.which("codex")

    def run(self, task: Task, workdir: Path) -> AgentRun:
        if not self.bin:
            return AgentRun(ok=False, usage=Usage(), error="未找到 codex CLI,跳过")
        usage = Usage()
        t0 = time.time()
        env = {
            **os.environ,
            "DEEPSEEK_API_KEY": providers.DEEPSEEK_KEY or "",
        }
        args = [
            self.bin, "exec", "--json",
            "--skip-git-repo-check",
            "--full-auto",
            "-c", "model_provider=deepseek",
            "-c", f"model={providers.DEEPSEEK_MODEL}",
        ]
        # 推理强度受控开关:不设则用 codex 默认(medium,会产生 reasoning token);
        # 设 none/minimal 可做归一化对照实验(ARENA_CODEX_REASONING=none)
        reasoning = os.environ.get("ARENA_CODEX_REASONING")
        if reasoning:
            args += ["-c", f"model_reasoning_effort={reasoning}"]
        args.append(task.prompt)
        try:
            r = subprocess.run(
                args,
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=task.timeout_minutes * 60 + 60,
                env=env,
            )
        except subprocess.TimeoutExpired:
            return AgentRun(ok=False, usage=usage, error="codex CLI 超时")
        usage.seconds = time.time() - t0
        arena = workdir / ".arena"
        arena.mkdir(exist_ok=True)
        (arena / "codex.out").write_text(r.stdout, encoding="utf-8")

        total: dict = {}
        for line in r.stdout.splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            # 0.142:turn.completed 顶层带累计 usage;input 含 cached,口径对齐时扣除
            if ev.get("type") == "turn.completed":
                usage.calls += 1
                u = ev.get("usage")
                if isinstance(u, dict):
                    total = {
                        "input_tokens": int(u.get("input_tokens", 0) or 0),
                        "cached_input_tokens": int(u.get("cached_input_tokens", 0) or 0),
                        "output_tokens": int(u.get("output_tokens", 0) or 0),
                        "reasoning_output_tokens": int(
                            u.get("reasoning_output_tokens", 0) or 0
                        ),
                    }
        if total:
            cached = int(total.get("cached_input_tokens", 0) or 0)
            usage.input_tokens = max(0, int(total.get("input_tokens", 0) or 0) - cached)
            usage.output_tokens = int(total.get("output_tokens", 0) or 0)
            usage.cache_tokens = cached
            usage.reasoning_tokens = int(
                total.get("reasoning_output_tokens", 0) or 0
            )
        return AgentRun(
            ok=r.returncode == 0,
            usage=usage,
            transcript=arena / "codex.out",
            error=(r.stderr.strip()[-500:] or None) if r.returncode != 0 else None,
        )
