import random
import time

import pytest

from slide import sliding_max


def brute(a, k):
    return [max(a[i : i + k]) for i in range(len(a) - k + 1)]


def test_fixed():
    assert sliding_max([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
    assert sliding_max([5], 1) == [5]
    assert sliding_max([2, 1], 2) == [2]


@pytest.mark.parametrize("k", [0, -1, 4])
def test_bad_k(k):
    with pytest.raises(ValueError):
        sliding_max([1, 2, 3], k)


def test_random_against_brute():
    random.seed(21)
    for _ in range(60):
        n = random.randint(1, 200)
        a = [random.randint(-50, 50) for _ in range(n)]
        k = random.randint(1, n)
        assert sliding_max(a, k) == brute(a, k)


def test_big_fast():
    random.seed(22)
    a = [random.randint(-10**9, 10**9) for _ in range(200_000)]
    k = 5_000
    t0 = time.time()
    got = sliding_max(a, k)
    dt = time.time() - t0
    assert len(got) == len(a) - k + 1
    assert dt < 3, f"太慢: {dt:.1f}s,应为 O(n)"
    # 抽查若干窗口
    for i in random.sample(range(len(got)), 50):
        assert got[i] == max(a[i : i + k])
