import random

from pairsum import pair_sum


def brute(nums, target):
    n = len(nums)
    cands = sorted(
        (min(nums[i], nums[j]), max(nums[i], nums[j]))
        for i in range(n)
        for j in range(i + 1, n)
        if nums[i] + nums[j] == target
    )
    return cands[0] if cands else None


def test_basic():
    assert pair_sum([2, 7, 11, 15], 9) == (2, 7)
    assert pair_sum([3, 2, 4], 6) == (2, 4)


def test_none():
    assert pair_sum([1, 2], 100) is None
    assert pair_sum([], 5) is None


def test_tie_break():
    assert pair_sum([1, 5, 4, 0, 3], 5) == (0, 5)
    assert pair_sum([-3, 8, 2, -7], -10) == (-7, -3)


def test_random_against_brute():
    random.seed(9)
    for _ in range(200):
        nums = [random.randint(-20, 20) for _ in range(random.randint(2, 25))]
        t = random.randint(-20, 20)
        assert pair_sum(nums, t) == brute(nums, t)
