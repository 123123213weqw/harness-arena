import random
import time
from itertools import permutations

from topo import topo_order


def brute(n, edges):
    es = set(edges)
    orders = []
    for perm in permutations(range(n)):
        pos = {v: i for i, v in enumerate(perm)}
        if all(pos[a] < pos[b] for a, b in es):
            orders.append(list(perm))
            if len(orders) > 1:
                return None
    return orders[0] if len(orders) == 1 else None


def test_fixed():
    assert topo_order(3, [(0, 1), (1, 2)]) == [0, 1, 2]
    assert topo_order(4, [(0, 1), (0, 2), (1, 3), (2, 3)]) is None  # 两种序
    assert topo_order(2, [(0, 1), (1, 0)]) is None                  # 环
    assert topo_order(1, []) == [0]
    assert topo_order(2, []) is None                                # 两个孤立点两种序
    assert topo_order(2, [(0, 1), (0, 1)]) == [0, 1]               # 重复边视为一条


def test_random_against_brute():
    random.seed(51)
    for _ in range(80):
        n = random.randint(1, 6)
        m = random.randint(0, 8)
        edges = [
            (random.randrange(n), random.randrange(n))
            for _ in range(m)
        ]
        edges = [(a, b) for a, b in edges if a != b]
        assert topo_order(n, edges) == brute(n, edges), (n, edges)


def test_big_chain_fast():
    n = 200_000
    edges = [(i, i + 1) for i in range(n - 1)]
    t0 = time.time()
    got = topo_order(n, edges)
    dt = time.time() - t0
    assert got == list(range(n))
    assert dt < 3, f"太慢: {dt:.1f}s,应 O(n+m)"
