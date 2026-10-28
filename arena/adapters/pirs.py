"""pi-rs(Rust 版 pi 0.74.2 复刻)适配器。

与 pi.py 同接法:非 TTY 一次性模式跑完即退;`--provider deepseek
--model deepseek-chat` 直连;DEEPSEEK_API_KEY 供 key;session jsonl 落在
--session-dir,usage 字段(input/output/cacheRead/cacheWrite/totalTokens)与
pi 同口径,据此记账。
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

PIRS_BIN = os.environ.get("PIRS_BIN", "pi-rs")


def _num(d: dict, *names: str) -> int:
    for n in names:
        v = d.get(n)
        if isinstance(v, (int, float)):
            return int(v)
    return 0


class PirsAdapter:
    name = "pirs"
    model = providers.DEEPSEEK_MODEL

    def run(self, task: Task, workdir: Path) -> AgentRun:
        bin_path = shutil.which(PIRS_BIN)
        if not bin_path:
            return AgentRun(ok=False, usage=Usage(), error=f"未找到 pi-rs: {PIRS_BIN}")
        usage = Usage()
        sdir = (workdir / ".arena" / "pirs-session").resolve()
        sdir.mkdir(parents=True, exist_ok=True)
        t0 = time.time()
        env = {**os.environ, "DEEPSEEK_API_KEY": providers.DEEPSEEK_KEY or ""}
        args = [
            bin_path,
            "--provider", "deepseek",
            "--model", providers.DEEPSEEK_MODEL,
            "--session-dir", str(sdir),
        ]
        # 思考档位透传(pi-rs 接受该 flag;deepseek-chat 的 chat 端点不认,同 pi)
        thinking = os.environ.get("ARENA_PIRS_THINKING")
        if thinking:
            args += ["--thinking", thinking]
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
            return AgentRun(ok=False, usage=usage, error="pi-rs 超时")
        usage.seconds = time.time() - t0
        out_path = workdir / ".arena" / "pirs.out"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(r.stdout, encoding="utf-8")

        sessions = sorted(sdir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
        transcript = sessions[-1] if sessions else out_path
        for line in (sessions[-1].read_text(encoding="utf-8").splitlines() if sessions else []):
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue
            if entry.get("type") != "message":
                continue
            msg = entry.get("message") or {}
            if msg.get("role") != "assistant":
                continue
            u = msg.get("usage") or {}
            if _num(u, "input", "inputTokens", "input_tokens") or _num(
                u, "output", "outputTokens", "output_tokens"
            ):
                usage.calls += 1
                usage.input_tokens += _num(u, "input", "inputTokens", "input_tokens")
                usage.output_tokens += _num(u, "output", "outputTokens", "output_tokens")
                usage.cache_tokens += _num(u, "cacheRead", "cache_read", "cacheReadTokens")
                usage.reasoning_tokens += _num(u, "reasoningTokens", "reasoning_tokens")
        return AgentRun(
            ok=r.returncode == 0,
            usage=usage,
            transcript=transcript,
            error=(r.stderr.strip()[-400:] or None) if r.returncode != 0 else None,
        )
