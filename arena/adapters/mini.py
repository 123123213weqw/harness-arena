"""mini:自研裸 agent 基线(对标 mini-swe-agent)。

每轮让模型输出一条 bash 命令,在工作区执行后把截断输出喂回去,
模型输出 DONE 或达到轮数上限即停。这是"几乎没有 harness 工程"的下界,
真实 harness 的分数减去它,才是 harness 工程本身的贡献。

LLM 走任意 OpenAI 兼容 API,环境变量:
    ARENA_API_BASE   默认 https://open.bigmodel.cn/api/paas/v4(智谱 GLM)
    ARENA_API_KEY    必填(回退读 ZHIPUAI_API_KEY / OPENAI_API_KEY)
    ARENA_MODEL      默认 glm-5.3
在 V100 上可把 ARENA_API_BASE 指向本地 Ollama/llama-server 实现零成本跑分。
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.request
from pathlib import Path

from ..schema import Task
from .base import AgentRun, Usage

BASE = os.environ.get("ARENA_API_BASE", "https://open.bigmodel.cn/api/paas/v4")
MODEL = os.environ.get("ARENA_MODEL", "glm-5.3")

MAX_TURNS = 15
CMD_TIMEOUT = 120
OUT_LIMIT = 4000

SYSTEM_PROMPT = (
    "你是一个工作在当前目录的终端编程 agent。每轮只输出一条要执行的 bash 命令,"
    "用 ```bash 代码块包裹;系统会执行并把输出(可能截断)返回给你。"
    "任务完成、或确认无法继续时,单独输出 DONE。不要输出多余解释。"
)

_BASH_RE = re.compile(r"```(?:bash|sh|shell)?\s*\n(.*?)```", re.S)


def _log(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _chat(messages: list[dict]) -> tuple[str, int, int]:
    # 本地 llama-server/Ollama 不校验鉴权,占位 key 直通;云端 API 缺 key 会收到 401 并记录为该题 error
    key = (
        os.environ.get("ARENA_API_KEY")
        or os.environ.get("ZHIPUAI_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or "sk-none"
    )
    req = urllib.request.Request(
        BASE.rstrip("/") + "/chat/completions",
        data=json.dumps(
            {
                "model": MODEL,
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 2048,
            }
        ).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.loads(r.read())
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {}) or {}
    return (
        content,
        int(usage.get("prompt_tokens", 0) or 0),
        int(usage.get("completion_tokens", 0) or 0),
    )


class MiniAdapter:
    name = "mini"
    model = MODEL

    def run(self, task: Task, workdir: Path) -> AgentRun:
        usage = Usage()
        transcript = workdir / ".arena" / "transcript.jsonl"
        messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"工作目录: {workdir}\n\n任务:\n{task.prompt}",
            },
        ]
        err: str | None = None
        try:
            for turn in range(MAX_TURNS):
                reply, pt, ct = _chat(messages)
                usage.calls += 1
                usage.input_tokens += pt
                usage.output_tokens += ct
                messages.append({"role": "assistant", "content": reply})
                _log(transcript, {"turn": turn, "role": "assistant", "content": reply})

                if "DONE" in reply:
                    break
                m = _BASH_RE.search(reply)
                if not m:
                    messages.append(
                        {"role": "user", "content": "请给出一个 ```bash 代码块,或单独输出 DONE。"}
                    )
                    continue
                cmd = m.group(1).strip()
                try:
                    r = subprocess.run(
                        ["bash", "-c", cmd],
                        cwd=workdir,
                        capture_output=True,
                        text=True,
                        timeout=CMD_TIMEOUT,
                    )
                    out = r.stdout
                    if r.stderr:
                        out += "\n[stderr]\n" + r.stderr
                    out = out[:OUT_LIMIT] or "(无输出)"
                except subprocess.TimeoutExpired:
                    out = f"(命令超时 {CMD_TIMEOUT}s 被杀)"
                messages.append({"role": "user", "content": f"$ {cmd}\n{out}"})
                _log(transcript, {"turn": turn, "role": "user", "cmd": cmd, "output": out})
        except Exception as e:  # 网络/协议错误:保留已累积 usage,标记错误
            err = f"mini agent error: {e!r}"
        return AgentRun(ok=err is None, usage=usage, transcript=transcript, error=err)
