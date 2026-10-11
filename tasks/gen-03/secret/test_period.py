import random
import time

import pytest

from period import minimal_period


def brute(s):
    n = len(s)
    for p in range(1, n + 1):
        if n % p == 0 and s[:p] * (n // p) == s:
            return p
    raise AssertionError


def test_fixed():
    assert minimal_period("aaaa") == 1
    assert minimal_period("abab") == 2
    assert minimal_period("abc") == 3
    assert minimal_period("aba") == 3
    assert minimal_period("abcabcabc") == 3
    assert minimal_period("x") == 1


def test_empty_raises():
    with pytest.raises(ValueError):
        minimal_period("")


def test_random_against_brute():
    random.seed(53)
    for _ in range(400):
        s = "".join(random.choice("ab") for _ in range(random.randint(1, 14)))
        assert minimal_period(s) == brute(s), s
    for _ in range(50):
        t = "".join(random.choice("abc") for _ in range(random.randint(1, 5)))
        s = t * random.randint(1, 5)
        assert minimal_period(s) == brute(s), s


def test_big_fast():
    rng = random.Random(7)
    s = "".join(rng.choice("abcdefghij") for _ in range(148_000))  # 近乎必然非周期
    t0 = time.time()
    got = minimal_period(s)
    dt = time.time() - t0
    assert got == len(s)
    assert dt < 2, f"太慢: {dt:.1f}s"
