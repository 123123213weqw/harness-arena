import random
import time
from collections import deque

from dsu import UnionFind


def brute_connected(edges, a, b):
    adj = {}
    for u, v in edges:
        adj.setdefault(u, set()).add(v)
        adj.setdefault(v, set()).add(u)
    seen = {a}
    q = deque([a])
    while q:
        u = q.popleft()
        if u == b:
            return True
        for v in adj.get(u, ()):
            if v not in seen:
                seen.add(v)
                q.append(v)
    return b in seen


def test_basic():
    uf = UnionFind(4)
    assert uf.count() == 4
    assert not uf.connected(0, 3)
    uf.union(0, 1)
    uf.union(1, 2)
    assert uf.connected(0, 2)
    assert uf.count() == 2
    uf.union(0, 2)  # 已同组
    assert uf.count() == 2


def test_random_against_brute():
    random.seed(52)
    for _ in range(30):
        n = random.randint(2, 9)
        uf = UnionFind(n)
        edges = []
        for _ in range(random.randint(0, 20)):
            a, b = random.randrange(n), random.randrange(n)
            uf.union(a, b)
            edges.append((a, b))
            x, y = random.randrange(n), random.randrange(n)
            assert uf.connected(x, y) == brute_connected(edges, x, y)
        comp = set()
        for x in range(n):
            for y in range(n):
                if uf.connected(x, y):
                    comp.add(min(x, y))
                    break
        assert uf.count() == len(comp)


def test_big_chain_fast():
    n = 200_000
    uf = UnionFind(n)
    t0 = time.time()
    for i in range(n - 1):
        uf.union(i, i + 1)
    assert uf.connected(0, n - 1)
    assert uf.count() == 1
    for i in range(0, n, 7):
        assert uf.connected(i, min(i + 3, n - 1))
    dt = time.time() - t0
    assert dt < 3, f"太慢: {dt:.1f}s,需按大小合并+路径压缩"
