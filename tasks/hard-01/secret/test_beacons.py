import random
import time

from beacons import count_beacons


def brute(N, k):
    return sum(
        1
        for x in range(1, N + 1)
        if sum(map(int, str(x))) % k == 0 and "13" not in str(x)
    )


def test_fixed():
    assert count_beacons(13, 1) == 12          # 13 被排除
    assert count_beacons(135, 1) == 127        # 排除 13,113,130..135 共 8 个
    assert count_beacons(9, 3) == 3            # 3,6,9
    assert count_beacons(1, 7) == 0
    assert count_beacons(7, 7) == 1


def test_random_against_brute():
    random.seed(31)
    for _ in range(40):
        N = random.randint(1, 10**5)
        k = random.randint(1, 13)
        assert count_beacons(N, k) == brute(N, k), (N, k)


def test_crossing_13_variants():
    for N in (129, 130, 131, 139, 213, 2130):
        assert count_beacons(N, 1) == brute(N, 1), N


def test_big_fast():
    t0 = time.time()
    got = count_beacons(10**18, 7)
    dt = time.time() - t0
    assert dt < 3, f"太慢: {dt:.1f}s,应数位 DP"
    assert isinstance(got, int) and 0 < got < 10**18
