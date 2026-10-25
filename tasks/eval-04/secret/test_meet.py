import random
import time

import pytest

from meet import common_free


def brute(busy_by_person, window, min_len):
    ws, we = window
    free = []
    for t in range(ws, we):
        ok = all(
            not any(s <= t < e for s, e in person)
            for person in busy_by_person
        )
        free.append(ok)
    out = []
    i = 0
    while i < len(free):
        if free[i]:
            j = i
            while j < len(free) and free[j]:
                j += 1
            if j - i >= min_len:
                out.append((ws + i, ws + j))
            i = j
        else:
            i += 1
    return out


def test_basic_two_persons():
    busy = [
        [(0, 10), (20, 30)],
        [(5, 15)],
    ]
    assert common_free(busy, (0, 40), 1) == [(15, 20), (30, 40)]
    assert common_free(busy, (0, 40), 5) == [(15, 20), (30, 40)]
    assert common_free(busy, (0, 40), 6) == [(30, 40)]
    assert common_free(busy, (0, 40), 11) == []


def test_adjacent_merge():
    busy = [[(10, 20)], [(30, 40)]]  # 两个不同人断开不同段,不相连
    assert common_free(busy, (0, 50), 1) == [(0, 10), (20, 30), (40, 50)]
    # 空闲 [20,30) 与 [40,50) 不相邻,不合并;但单人时忙碌区间相邻应让空闲保持极大
    assert common_free([[(10, 20), (20, 25)]], (0, 30), 1) == [(0, 10), (25, 30)]


def test_empty_and_degenerate_intervals():
    assert common_free([[], []], (0, 10), 10) == [(0, 10)]
    assert common_free([[ (3, 3) ]], (0, 10), 1) == [(0, 10)]  # 空区间不占时间
    assert common_free([], (0, 10), 5) == [(0, 10)]


def test_out_of_window_ignored():
    assert common_free([[(-100, -1), (100, 200)]], (0, 50), 1) == [(0, 50)]


def test_fully_covered():
    assert common_free([[(0, 100)], [(10, 90)]], (20, 30), 1) == []


def test_bad_params():
    with pytest.raises(ValueError):
        common_free([[]], (10, 0), 1)
    with pytest.raises(ValueError):
        common_free([[]], (0, 10), 0)


def test_unsorted_overlapping_input():
    busy = [[(30, 40), (0, 10), (5, 15)]]
    assert common_free(busy, (0, 50), 1) == [(15, 30), (40, 50)]


def test_random_against_brute():
    random.seed(111)
    for _ in range(60):
        span = random.randint(20, 60)
        ws = random.randint(0, 5)
        we = ws + span
        persons = []
        for _ in range(random.randint(1, 3)):
            ivs = []
            for _ in range(random.randint(0, 8)):
                a = random.randint(ws, we)
                b = random.randint(a, we)
                ivs.append((a, b))
            persons.append(ivs)
        min_len = random.randint(1, 8)
        assert common_free(persons, (ws, we), min_len) == brute(persons, (ws, we), min_len)


def test_big_fast():
    random.seed(112)
    persons = [
        sorted(
            (random.randint(0, 10**9), 0) for _ in range(100_000)
        )
    ]
    persons = [
        [(s, s + random.randint(1, 1000)) for s, _ in person]
        for person in [persons[0], list(reversed(persons[0]))]
    ]
    t0 = time.time()
    out = common_free(persons, (0, 10**9 + 10**4), 60)
    dt = time.time() - t0
    assert dt < 3, f"太慢: {dt:.1f}s,应 O(B log B)"
    assert all(b - a >= 60 for a, b in out)
    assert out == sorted(out)
