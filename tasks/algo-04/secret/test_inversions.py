import random
import time

from inversions import count_inversions


def brute(a):
    return sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] > a[j])


def test_fixed():
    assert count_inversions([]) == 0
    assert count_inversions([1]) == 0
    assert count_inversions([2, 1]) == 1
    assert count_inversions([3, 2, 1]) == 3
    assert count_inversions([1, 2, 3]) == 0
    assert count_inversions([2, 2, 2]) == 0


def test_random_against_brute():
    random.seed(13)
    for _ in range(40):
        a = [random.randint(-100, 100) for _ in range(random.randint(0, 300))]
        assert count_inversions(a) == brute(a)


def test_big_desc_exact():
    n = 200_000
    t0 = time.time()
    got = count_inversions(list(range(n, 0, -1)))
    dt = time.time() - t0
    assert dt < 5, f"太慢: {dt:.1f}s,应为 O(n log n)"
    assert got == n * (n - 1) // 2
