import random

from algo import max_subarray_sum


def brute(a):
    return max(
        sum(a[i:j]) for i in range(len(a)) for j in range(i + 1, len(a) + 1)
    )


def test_basic():
    assert max_subarray_sum([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6


def test_all_negative():
    assert max_subarray_sum([-5, -2, -9]) == -2


def test_single():
    assert max_subarray_sum([42]) == 42


def test_all_positive():
    assert max_subarray_sum([1, 2, 3]) == 6


def test_random_against_brute():
    random.seed(7)
    a = [random.randint(-50, 50) for _ in range(300)]
    assert max_subarray_sum(a) == brute(a)
