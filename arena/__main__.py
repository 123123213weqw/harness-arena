"""CLI 入口。

用法:
    python3 -m arena --adapters mock
    ARENA_API_KEY=xxx python3 -m arena --adapters mini
    python3 -m arena --adapters mock,mini --repeats 3
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from .adapters import build
from .report import print_report
from .runner import run_one
from .schema import load_suite
from .store import Store


def main() -> None:
    ap = argparse.ArgumentParser(prog="arena")
    ap.add_argument("--tasks-dir", default="tasks")
    ap.add_argument("--only", default=None, help="只跑这些题(逗号分隔 id 子串匹配)")
    ap.add_argument("--adapters", default="mock", help="逗号分隔:mock,mini,claude,codex")
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--db", default="runs/arena.db")
    ap.add_argument("--workspaces", default="runs/workspaces")
    args = ap.parse_args()

    tasks = load_suite(Path(args.tasks_dir))
    if args.only:
        keys = [k.strip() for k in args.only.split(",") if k.strip()]
        tasks = [t for t in tasks if any(k in t.id for k in keys)]
    names = [n.strip() for n in args.adapters.split(",") if n.strip()]
    print(f"载入 {len(tasks)} 题 × adapters={names} × repeats={args.repeats}")

    suite = time.strftime("%Y%m%d-%H%M%S")
    wsroot = Path(args.workspaces)
    wsroot.mkdir(parents=True, exist_ok=True)
    store = Store(args.db)

    results = []
    for name in names:
        adapter = build(name)
        for task in tasks:
            for i in range(args.repeats):
                r = run_one(task, adapter, wsroot, repeat=i)
                results.append(r)
                store.add({
                    "suite": suite,
                    "task_id": task.id,
                    "domain": task.domain,
                    "difficulty": task.difficulty,
                    "adapter": r.adapter,
                    "model": r.model,
                    "repeat": r.repeat,
                    "status": r.status,
                    "passed": r.passed,
                    "points": r.points,
                    "input_tokens": r.usage.input_tokens,
                    "output_tokens": r.usage.output_tokens,
                    "cache_tokens": r.usage.cache_tokens,
                    "reasoning_tokens": r.usage.reasoning_tokens,
                    "calls": r.usage.calls,
                    "seconds": r.usage.seconds,
                    "workspace": str(r.workspace),
                    "error": r.error,
                })
                print(
                    f"[{r.status:^13}] {task.id:<14} {r.adapter:<12} "
                    f"in={r.usage.input_tokens:<7} cache={r.usage.cache_tokens:<7} "
                    f"out={r.usage.output_tokens:<7} {r.usage.seconds:5.1f}s "
                    f"{r.error or ''}",
                    flush=True,
                )
    store.close()
    print_report(results)


if __name__ == "__main__":
    main()
