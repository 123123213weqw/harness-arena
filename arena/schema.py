"""任务定义、加载与校验。

题目目录约定:
    tasks/<task-id>/
      task.yaml    元信息
      prompt.md    给 agent 的题目描述
      env/         拷入工作区的初始文件(对 agent 可见)
      secret/      判定材料,只在判定阶段拷入(对 agent 不可见)
      mock/        参考解,仅 mock adapter 使用,永不进工作区
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

DOMAINS = ("coding", "ops", "algo", "math", "frontend", "data", "composite", "computer-use")
VERIFIERS = ("pytest", "answer", "script", "human")


@dataclass
class Task:
    root: Path
    id: str
    domain: str
    difficulty: int  # 1-5
    prompt: str
    verifier: str
    points: float
    timeout_minutes: int
    setup: Path | None = None   # env/
    secret: Path | None = None  # secret/
    mock: Path | None = None    # mock/


def _opt_dir(root: Path, name: str) -> Path | None:
    p = root / name
    return p if p.is_dir() else None


def load_task(root: Path) -> Task:
    cfg = yaml.safe_load((root / "task.yaml").read_text(encoding="utf-8"))
    task_id = cfg.get("id", root.name)
    domain = cfg.get("domain")
    verifier = cfg.get("verifier", "pytest")
    if domain not in DOMAINS:
        raise ValueError(f"{root}: domain 必须是 {DOMAINS} 之一,得到 {domain!r}")
    if verifier not in VERIFIERS:
        raise ValueError(f"{root}: verifier 必须是 {VERIFIERS} 之一,得到 {verifier!r}")
    prompt = (root / "prompt.md").read_text(encoding="utf-8")
    return Task(
        root=root,
        id=task_id,
        domain=domain,
        difficulty=int(cfg.get("difficulty", 3)),
        prompt=prompt,
        verifier=verifier,
        points=float(cfg.get("points", 1.0)),
        timeout_minutes=int(cfg.get("timeout_minutes", 10)),
        setup=_opt_dir(root, cfg.get("setup_dir", "env")),
        secret=_opt_dir(root, cfg.get("secret_dir", "secret")),
        mock=_opt_dir(root, cfg.get("mock_dir", "mock")),
    )


def load_suite(tasks_dir: Path) -> list[Task]:
    tasks = [
        load_task(d)
        for d in sorted(tasks_dir.iterdir())
        if d.is_dir() and (d / "task.yaml").is_file()
    ]
    return sorted(tasks, key=lambda t: (t.domain, t.id))
