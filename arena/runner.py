"""单次执行:准备干净工作区 → adapter 干活 → 判定 → 产出 RunResult。"""
from __future__ import annotations

import shutil
import time
from dataclasses import dataclass
from pathlib import Path

from .adapters.base import Adapter, AgentRun, Usage
from .schema import Task
from .verifier import Verdict, verify


@dataclass
class RunResult:
    task: Task
    adapter: str
    model: str
    repeat: int
    status: str
    passed: bool | None
    points: float
    usage: Usage
    workspace: Path
    error: str | None


def run_one(task: Task, adapter: Adapter, runroot: Path, repeat: int = 0) -> RunResult:
    ws = runroot / task.id / adapter.name / f"run{repeat}"
    if ws.exists():
        shutil.rmtree(ws)
    ws.mkdir(parents=True)
    ws = ws.resolve()  # 绝对路径:子进程 cwd 变化时相对路径会被二次拼接
    if task.setup:
        shutil.copytree(task.setup, ws, dirs_exist_ok=True)

    t0 = time.time()
    try:
        ar: AgentRun = adapter.run(task, ws)
        adapter_error = ar.error
    except Exception as e:  # adapter 崩溃也要继续判定,拿到失败记录
        ar = AgentRun(ok=False, usage=Usage(), error=f"adapter crash: {e!r}")
        adapter_error = ar.error
    usage = ar.usage
    usage.seconds = time.time() - t0

    try:
        v: Verdict = verify(task, ws)
    except Exception as e:
        v = Verdict(None, "error", f"verifier crash: {e!r}")

    passed = {"pass": True, "fail": False}.get(v.status)
    points = task.points if passed is True else 0.0
    error = adapter_error or (v.detail if v.status == "error" else None)
    return RunResult(
        task=task,
        adapter=adapter.name,
        model=getattr(adapter, "model", ""),
        repeat=repeat,
        status=v.status,
        passed=passed,
        points=points,
        usage=usage,
        workspace=ws,
        error=error,
    )
