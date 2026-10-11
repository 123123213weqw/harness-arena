import random
import time

from lis import lis_length


def brute(a):
    if not a:
        return 0
    best = [1] * len(a)
    for i in range(len(a)):
        for j in range(i):
            if a[j] < a[i]:
                best[i] = max(best[i], best[j] + 1)
    return max(best)


def test_fixed():
    assert lis_length([]) == 0
    assert lis_length([10]) == 1
    assert lis_length([10, 9, 2, 5, 3, 7, 101, 18]) == 4
    assert lis_length([7, 7, 7, 7]) == 1
    assert lis_length([1, 2, 3, 4]) == 4
    assert lis_length([4, 3, 2, 1]) == 1


def test_random_against_brute():
    random.seed(3)
    for _ in range(30):
        a = [random.randint(-100, 100) for _ in range(random.randint(1, 80))]
        assert lis_length(a) == brute(a)


def test_big_fast():
    random.seed(5)
    a = [random.randint(0, 10**6) for _ in range(3000)]
    t0 = time.time()
    got = lis_length(a)
    dt = time.time() - t0
    assert dt < 3, f"太慢: {dt:.1f}s,应为 O(n log n)"
    assert got == brute(a)
