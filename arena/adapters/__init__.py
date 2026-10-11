"""adapter 注册表。新增 harness:实现 Adapter 协议,注册进来即可。"""
from __future__ import annotations

from .base import AgentRun, Adapter, Usage
from .claude import ClaudeCodeAdapter
from .codex import CodexAdapter
from .mini import MiniAdapter
from .mock import MockAdapter
from .xharness import XHarnessAdapter

REGISTRY: dict[str, type] = {
    "mock": MockAdapter,
    "mini": MiniAdapter,
    "claude": ClaudeCodeAdapter,
    "claude-code": ClaudeCodeAdapter,  # 别名
    "codex": CodexAdapter,
    "xharness": XHarnessAdapter,
}

try:  # pi 依赖外部 CLI,装好才注册
    from .pi import PiAdapter

    REGISTRY["pi"] = PiAdapter
except ImportError:  # pragma: no cover
    pass


def build(name: str) -> Adapter:
    if name not in REGISTRY:
        raise KeyError(f"未知 adapter {name!r},可选: {sorted(REGISTRY)}")
    return REGISTRY[name]()  # type: ignore[return-value]
