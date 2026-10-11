"""mock harness:直接把题目 mock/ 参考解拷进工作区。

用途:验证「工作区准备 → 判定 → 记账 → 报表」整条管线,不花一分钱 token。
mock/ 永远不会被拷进真实 harness 的工作区,不存在污染。
"""
from __future__ import annotations

import shutil
from pathlib import Path

from ..schema import Task
from .base import AgentRun, Usage


class MockAdapter:
    name = "mock"
    model = "mock"

    def run(self, task: Task, workdir: Path) -> AgentRun:
        if task.mock:
            shutil.copytree(task.mock, workdir, dirs_exist_ok=True)
            return AgentRun(ok=True, usage=Usage())
        return AgentRun(
            ok=False,
            usage=Usage(),
            error="题目无 mock/ 参考解,空跑(预期 fail)",
        )
