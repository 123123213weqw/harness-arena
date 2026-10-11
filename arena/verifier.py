"""判定器:agent 跑完后在工作区上自动判分。

- pytest:  把 secret/ 拷入工作区后运行 pytest,退出码 0 为 pass
- answer:  从 secret/expected_answer.py 里 exec 出 EXPECTED,与工作区 answer.txt 精确比对
- script:  把 secret/ 拷入工作区后执行 secret/verify.sh(bash,cwd=工作区),退出码 0 为 pass
- human:   不自动判分,标记 pending_human,进人工/盲投队列
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .schema import Task

TASK_PY = os.environ.get("ARENA_TASK_PYTHON", sys.executable)


@dataclass
class Verdict:
    passed: bool | None  # None = 待人工
    status: str          # pass | fail | pending_human | error
    detail: str


def verify(task: Task, ws: Path) -> Verdict:
    if task.verifier == "pytest":
        return _pytest(task, ws)
    if task.verifier == "answer":
        return _answer(task, ws)
    if task.verifier == "script":
        return _script(task, ws)
    return Verdict(None, "pending_human", "前端/设计类题目等待人类盲投评分")


def _copy_secret(task: Task, ws: Path) -> Path:
    dst = ws / task.secret.name
    shutil.copytree(task.secret, dst, dirs_exist_ok=True)
    return dst


def _run(cmd: list[str], cwd: Path, timeout: int) -> tuple[int, str]:
    env = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    r = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env
    )
    out = (r.stdout + ("\n[stderr]\n" + r.stderr if r.stderr else ""))[-2000:]
    return r.returncode, out


def _pytest(task: Task, ws: Path) -> Verdict:
    if not task.secret:
        return Verdict(False, "error", "题目缺 secret/,无法判定")
    _copy_secret(task, ws)
    try:
        code, out = _run(
            [TASK_PY, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider"],
            ws,
            task.timeout_minutes * 60,
        )
    except subprocess.TimeoutExpired as e:
        return Verdict(False, "error", f"pytest 超时: {e}")
    ok = code == 0
    return Verdict(ok, "pass" if ok else "fail", out)


def _answer(task: Task, ws: Path) -> Verdict:
    exp_file = task.secret / "expected_answer.py" if task.secret else None
    if not exp_file or not exp_file.is_file():
        return Verdict(False, "error", "题目缺 secret/expected_answer.py")
    ns: dict = {}
    exec(exp_file.read_text(encoding="utf-8"), ns)  # noqa: S102 - 受信题库
    expected = str(ns["EXPECTED"]).strip()
    f = ws / "answer.txt"
    if not f.is_file():
        return Verdict(False, "fail", "工作区未生成 answer.txt")
    got = f.read_text(encoding="utf-8").strip()
    ok = got == expected
    return Verdict(ok, "pass" if ok else "fail", f"expected={expected} got={got[:80]!r}")


def _script(task: Task, ws: Path) -> Verdict:
    if not task.secret:
        return Verdict(False, "error", "题目缺 secret/,无法判定")
    _copy_secret(task, ws)
    script = (ws / task.secret.name / "verify.sh").resolve()
    if not script.is_file():
        return Verdict(False, "error", "secret/ 里缺 verify.sh")
    try:
        code, out = _run(["bash", str(script)], ws, task.timeout_minutes * 60)
    except subprocess.TimeoutExpired as e:
        return Verdict(False, "error", f"verify.sh 超时: {e}")
    ok = code == 0
    return Verdict(ok, "pass" if ok else "fail", out)
