import math
import random
import time

from bigcomb import comb_mod

MOD = 998244353


def test_edges():
    assert comb_mod(5, 0) == 1
    assert comb_mod(10**18, 0) == 1
    assert comb_mod(5, 6) == 0
    assert comb_mod(5, -1) == 0
    assert comb_mod(5, 5) == 1


def test_random_against_math_comb():
    random.seed(35)
    for _ in range(80):
        n = random.randint(1, 3000)
        r = random.randint(0, n)
        assert comb_mod(n, r) == math.comb(n, r) % MOD, (n, r)


def test_asymmetry_hint():
    # r 和 n-r 等价:大 n 时只有小 r 可直接对照对称性
    assert comb_mod(10**6 + 5, 3) == math.comb(10**6 + 5, 3) % MOD


def test_huge_fast():
    t0 = time.time()
    got = comb_mod(10**18, 10**6)
    dt = time.time() - t0
    assert dt < 3, f"太慢: {dt:.1f}s,应为 O(r) 乘法逆元,不能展开大整数"
    assert 0 <= got < MOD
