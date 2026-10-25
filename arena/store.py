"""SQLite 结果存储:每次 run 一行,token/时长全记,便于出榜与回溯。"""
from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any

DDL = """
create table if not exists runs (
    id integer primary key,
    ts real,
    suite text,
    task_id text,
    domain text,
    difficulty int,
    adapter text,
    model text,
    repeat int,
    status text,
    passed int,
    points real,
    input_tokens int,
    output_tokens int,
    cache_tokens int,
    reasoning_tokens int,
    calls int,
    seconds real,
    workspace text,
    error text
)
"""


class Store:
    def __init__(self, path: str | Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path), timeout=30.0)  # 并行双轮时等锁而非崩
        self.db.execute("PRAGMA busy_timeout=30000")
        self.db.execute(DDL)
        for col in ("cache_tokens", "reasoning_tokens"):  # 旧库迁移
            try:
                self.db.execute(f"alter table runs add column {col} int")
            except sqlite3.OperationalError:
                pass

    def add(self, row: dict[str, Any]) -> None:
        row = {"ts": time.time(), **row}
        cols = ",".join(row)
        ph = ",".join("?" for _ in row)
        self.db.execute(f"insert into runs({cols}) values({ph})", tuple(row.values()))
        self.db.commit()

    def close(self) -> None:
        self.db.commit()
        self.db.close()
