"""adapter 协议:harness 的统一抽象。

每个 adapter 代表一种「agent harness」——同一个模型换不同 harness,
或不同模型各自默认 harness,都在同一接口下跑同一套题。
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ..schema import Task


@dataclass
class Usage:
    input_tokens: int = 0      # 不含缓存读(与 xharness 口径一致,各家只记录不横比)
    output_tokens: int = 0
    cache_tokens: int = 0      # 缓存读
    reasoning_tokens: int = 0
    calls: int = 0             # provider 调用次数
    seconds: float = 0.0


@dataclass
class AgentRun:
    ok: bool
    usage: Usage
    transcript: Path | None = None
    error: str | None = None


class Adapter(Protocol):
    name: str
    model: str

    def run(self, task: Task, workdir: Path) -> AgentRun: ...
