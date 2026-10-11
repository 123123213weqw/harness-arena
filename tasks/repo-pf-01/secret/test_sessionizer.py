import random
import time

from sessionizer import sessionize


def oracle(lines, gap_seconds=1800):
    """独立实现:每用户只跟踪最近会话。"""
    out = {}
    cur = {}
    for ts, u in lines:
        if u in cur and ts - cur[u][1] <= gap_seconds:
            s, _e, c = cur[u]
            cur[u] = (s, ts, c + 1)
        else:
            if u in cur:
                out.setdefault(u, []).append(cur[u])
            cur[u] = (ts, ts, 1)
    for u, s in cur.items():
        out.setdefault(u, []).append(s)
    return out


def test_basic():
    lines = [(0, "a"), (10, "a"), (100, "a"), (5000, "a"), (0, "b")]
    assert sessionize(lines, gap_seconds=100) == {
        "a": [(0, 100, 3), (5000, 5000, 1)],
        "b": [(0, 0, 1)],
    }


def test_gap_boundary():
    lines = [(0, "a"), (60, "a"), (121, "a")]
    assert sessionize(lines, gap_seconds=60) == {"a": [(0, 60, 2), (121, 121, 1)]}


def test_empty():
    assert sessionize([], 30) == {}


def test_random_against_oracle():
    random.seed(61)
    for _ in range(50):
        n = random.randint(0, 400)
        ts_list = sorted(random.randint(0, 50000) for _ in range(n))
        lines = [(t, random.choice(["u1", "u2", "u3"])) for t in ts_list]
        gap = random.choice([10, 100, 1000, 100000])
        assert sessionize(lines, gap) == oracle(lines, gap)


def test_big_fast():
    random.seed(62)
    n = 200_000
    ts_list = sorted(random.randint(0, 30_000_000) for _ in range(n))
    lines = [(t, f"u{random.randint(0, 999)}") for t in ts_list]
    t0 = time.time()
    got = sessionize(lines, 300)
    dt = time.time() - t0
    assert dt < 4, f"太慢: {dt:.1f}s,应 O(n)"
    # 抽样核对与 oracle 一致(全量 oracle 也很快)
    assert got == oracle(lines, 300)
