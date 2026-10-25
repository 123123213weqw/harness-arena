"""回归对照:两个 suite 逐臂逐题对比,列出翻转。

用法:.venv/bin/python scripts/regression_diff.py <旧suite> <新suite> [--adapter xharness,...]
输出:每臂 总分变化 / 退化题(过→挂)/ 改善题(挂→过)/ 单发方差(不稳定题)。
"""
from __future__ import annotations

import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "runs" / "arena.db"


def load(db: sqlite3.Connection, suite: str):
    by: dict[tuple[str, str], list[str]] = defaultdict(list)
    for task, adapter, status in db.execute(
        "select task_id, adapter, status from runs where suite=? order by id",
        (suite,),
    ):
        by[(adapter, task)].append(status)
    return by


def solved(statuses: list[str]) -> bool:
    return any(s == "pass" for s in statuses)


def stable(statuses: list[str]) -> bool:
    return bool(statuses) and all(s == "pass" for s in statuses)


def main() -> None:
    args = [a for a in sys.argv[1:]]
    adapters_filter = None
    if "--adapter" in args:
        i = args.index("--adapter")
        adapters_filter = set(args[i + 1].split(","))
        args = args[:i] + args[i + 2 :]
    if len(args) != 2:
        sys.exit("用法: regression_diff.py <旧suite> <新suite> [--adapter a,b]")
    old_suite, new_suite = args

    db = sqlite3.connect(DB)
    old, new = load(db, old_suite), load(db, new_suite)
    adapters = sorted({a for a, _ in new} | {a for a, _ in old})
    if adapters_filter:
        adapters = [a for a in adapters if a in adapters_filter]

    print(f"# 回归对照: {old_suite} → {new_suite}\n")
    for adapter in adapters:
        tasks = sorted({t for a, t in new if a == adapter} | {t for a, t in old if a == adapter})
        o_solved = {t for t in tasks if solved(old.get((adapter, t), []))}
        n_solved = {t for t in tasks if solved(new.get((adapter, t), []))}
        regressed = sorted(o_solved - n_solved)
        improved = sorted(n_solved - o_solved)
        unstable = sorted(
            t for t in tasks
            if t in o_solved and t in n_solved
            and (stable(old[(adapter, t)]) != stable(new[(adapter, t)]))
        )
        print(f"## {adapter}:解出 {len(o_solved)} → {len(n_solved)}"
              f"({'+' if len(n_solved) >= len(o_solved) else ''}{len(n_solved) - len(o_solved)})")
        if regressed:
            print(f"- 退化(过→挂): {', '.join(regressed)}")
        if improved:
            print(f"- 改善(挂→过): {', '.join(improved)}")
        if unstable:
            detail = ", ".join(
                f"{t}({'/'.join(old[(adapter, t)])}→{'/'.join(new[(adapter, t)])})"
                for t in unstable
            )
            print(f"- 稳定性翻转: {detail}")
        if not (regressed or improved or unstable):
            print("- 无逐题变化")
        print()


if __name__ == "__main__":
    main()
