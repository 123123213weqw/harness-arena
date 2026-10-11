import random
import time

from walks import count_walks

MOD = 998244353


def brute(n, edges, L, s, t, mod):
    cnt = [[0] * n for _ in range(n)]
    for u, v in edges:
        cnt[u][v] += 1
    dp = [0] * n
    dp[s] = 1
    for _ in range(L):
        nd = [0] * n
        for u in range(n):
            if dp[u]:
                for v in range(n):
                    if cnt[u][v]:
                        nd[v] = (nd[v] + dp[u] * cnt[u][v]) % mod
        dp = nd
    return dp[t] % mod


def test_fixed():
    assert count_walks(2, [(0, 1)], 1, 0, 1, MOD) == 1
    assert count_walks(2, [(0, 1)], 5, 0, 1, MOD) == 0
    assert count_walks(2, [(0, 1), (1, 0)], 4, 0, 0, MOD) == 1
    assert count_walks(1, [(0, 0)], 10**9, 0, 0, MOD) == 1
    assert count_walks(3, [], 0, 1, 2, MOD) == 0
    assert count_walks(3, [], 0, 2, 2, MOD) == 1
    assert count_walks(2, [(0, 1), (0, 1)], 1, 0, 1, MOD) == 2  # 重边各计


def test_random_against_brute():
    random.seed(33)
    for _ in range(40):
        n = random.randint(1, 8)
        m = random.randint(0, 14)
        edges = [
            (random.randrange(n), random.randrange(n)) for _ in range(m)
        ]
        L = random.randint(0, 40)
        s, t = random.randrange(n), random.randrange(n)
        assert count_walks(n, edges, L, s, t, MOD) == brute(
            n, edges, L, s, t, MOD
        ), (n, edges, L, s, t)


def test_big_fast():
    random.seed(34)
    n = 40
    edges = [(random.randrange(n), random.randrange(n)) for _ in range(300)]
    t0 = time.time()
    got = count_walks(n, edges, 10**9, 0, n - 1, MOD)
    dt = time.time() - t0
    assert dt < 5, f"太慢: {dt:.1f}s,应矩阵快速幂"
    assert 0 <= got < MOD
