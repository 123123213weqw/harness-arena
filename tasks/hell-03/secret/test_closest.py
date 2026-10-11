import random
import time

import pytest

from closest import closest_pair_sq


def brute(pts):
    return min(
        (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
        for i, a in enumerate(pts)
        for b in pts[i + 1 :]
    )


def test_fixed():
    assert closest_pair_sq([(0, 0), (3, 4)]) == 25
    assert closest_pair_sq([(0, 0), (1, 1), (4, 4)]) == 2
    assert closest_pair_sq([(-1, -1), (2, 3), (5, 8)]) == 25


def test_duplicates_zero():
    pts = [(7, 7), (0, 0), (7, 7), (100, 100)]
    assert closest_pair_sq(pts) == 0
    assert closest_pair_sq([(5, 5), (5, 5)]) == 0


def test_too_few_points():
    with pytest.raises(ValueError):
        closest_pair_sq([(1, 1)])
    with pytest.raises(ValueError):
        closest_pair_sq([])


def test_negative_and_large():
    pts = [(-10**9, -10**9), (10**9, 10**9), (0, 1), (0, -1)]
    assert closest_pair_sq(pts) == 4


def test_random_against_brute():
    random.seed(81)
    for _ in range(80):
        n = random.randint(2, 120)
        span = random.choice([5, 50, 10**9])
        pts = [
            (random.randint(-span, span), random.randint(-span, span))
            for _ in range(n)
        ]
        assert closest_pair_sq(pts) == brute(pts), pts


def test_two_clusters():
    random.seed(82)
    left = [(random.randint(0, 10), random.randint(0, 10)) for _ in range(150)]
    right = [(random.randint(10**6, 10**6 + 10), random.randint(0, 10)) for _ in range(150)]
    pts = left + right
    assert closest_pair_sq(pts) == brute(pts)


def test_big_fast():
    rng = random.Random(83)
    pts = [
        (rng.randint(-10**9, 10**9), rng.randint(-10**9, 10**9))
        for _ in range(300_000)
    ]
    t0 = time.time()
    got = closest_pair_sq(pts)
    dt = time.time() - t0
    assert dt < 10, f"太慢: {dt:.1f}s,应 O(n log n)(门槛按基准机校准)"
    assert isinstance(got, int) and got >= 0

    dense = [(rng.randint(0, 1000), rng.randint(0, 1000)) for _ in range(200_000)]
    t0 = time.time()
    assert closest_pair_sq(dense) == 0
    assert time.time() - t0 < 10
