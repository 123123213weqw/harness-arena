"""pi coding agent headless 适配(badlogic/pi-mono,@earendil-works/pi-coding-agent)。

已实测(pi 0.74.2):非 TTY 下 pi 自动进入一次性模式跑完即退,无需额外标志;
`--provider deepseek --model deepseek-chat` 直连,环境变量 DEEPSEEK_API_KEY 供 key。
session jsonl 落在 --session-dir,含每条 assistant 消息的 usage
(inputTokens/outputTokens/cacheReadTokens,与 xharness 同口径),据此记账。
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

PI_BIN = os.environ.get("PI_BIN", str(Path.home() / ".npm-global" / "bin" / "pi"))


def _num(d: dict, *names: str) -> int:
    for n in names:
        v = d.get(n)
        if isinstance(v, (int, float)):
            return int(v)
    return 0


class PiAdapter:
    name = "pi"
    model = providers.DEEPSEEK_MODEL

    def run(self, task: Task, workdir: Path) -> AgentRun:
        if not Path(PI_BIN).is_file() and not shutil.which("pi"):
            return AgentRun(ok=False, usage=Usage(), error=f"未找到 pi: {PI_BIN}")
        bin_path = Path(PI_BIN).as_posix() if Path(PI_BIN).is_file() else "pi"
        usage = Usage()
        sdir = (workdir / ".arena" / "pi-session").resolve()
        sdir.mkdir(parents=True, exist_ok=True)
        t0 = time.time()
        env = {**os.environ, "DEEPSEEK_API_KEY": providers.DEEPSEEK_KEY or ""}
        args = [
            bin_path,
            "--provider", "deepseek",
            "--model", providers.DEEPSEEK_MODEL,
            "--session-dir", str(sdir),
        ]
        # 思考档位受控开关:ARENA_PI_THINKING=high/off/...(pi 的 --thinking)
        thinking = os.environ.get("ARENA_PI_THINKING")
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
            return AgentRun(ok=False, usage=usage, error="pi 超时")
        usage.seconds = time.time() - t0
        out_path = workdir / ".arena" / "pi.out"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(r.stdout, encoding="utf-8")

        sessions = sorted(sdir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
        transcript = sessions[-1] if sessions else out_path
        if sessions:
            for line in sessions[-1].read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line.startswith("{"):
                    continue
                try:
                    msg = json.loads(line)
                except Exception:
                    continue
                u = msg.get("usage") or (msg.get("message") or {}).get("usage") or {}
                if isinstance(u, dict) and (
                    _num(u, "inputTokens", "input_tokens", "input")
                    or _num(u, "outputTokens", "output_tokens", "output")
                ):
                    usage.calls += 1
                    usage.input_tokens += _num(u, "inputTokens", "input_tokens", "input")
                    usage.output_tokens += _num(
                        u, "outputTokens", "output_tokens", "output"
                    )
                    usage.cache_tokens += _num(
                        u, "cacheReadTokens", "cache_read_tokens", "cacheRead"
                    )
                    usage.reasoning_tokens += _num(
                        u, "reasoningTokens", "reasoning_tokens", "reasoning"
                    )
        return AgentRun(
            ok=r.returncode == 0,
            usage=usage,
            transcript=transcript,
            error=(r.stderr.strip()[-400:] or None) if r.returncode != 0 else None,
        )
