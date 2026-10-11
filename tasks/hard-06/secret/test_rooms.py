import random
import time
from itertools import combinations

from rooms import max_value


def brute(intervals):
    best = 0
    n = len(intervals)
    for r in range(n + 1):
        for sub in combinations(intervals, r):
            ok = True
            for (s1, e1, _), (s2, e2, _) in combinations(sub, 2):
                if s1 < e2 and s2 < e1:
                    ok = False
                    break
            if ok:
                best = max(best, sum(v for _, _, v in sub))
    return best


def test_fixed():
    assert max_value([]) == 0
    assert max_value([(0, 10, 100)]) == 100
    assert max_value([(0, 10, 100), (10, 20, 50)]) == 150  # 端点相接不冲突
    assert max_value([(0, 10, 100), (5, 15, 200)]) == 200  # 真冲突取更优
    assert max_value([(0, 10, 5), (1, 2, 3), (2, 3, 4)]) == 7  # 短串不贪大


def test_random_against_brute():
    random.seed(41)
    for _ in range(80):
        n = random.randint(0, 12)
        ivs = []
        for _ in range(n):
            s = random.randint(0, 30)
            e = s + random.randint(1, 12)
            ivs.append((s, e, random.randint(1, 50)))
        assert max_value(ivs) == brute(ivs), ivs


def test_big_fast():
    random.seed(42)
    ivs = []
    t = 0
    for _ in range(200_000):
        s = t + random.randint(0, 3)
        e = s + random.randint(1, 1000)
        t = s
        ivs.append((s, e, random.randint(1, 10**6)))
    t0 = time.time()
    got = max_value(ivs)
    dt = time.time() - t0
    assert dt < 3, f"太慢: {dt:.1f}s,应 O(n log n) DP"
    assert got > 0
