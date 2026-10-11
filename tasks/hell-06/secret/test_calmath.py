import random
from datetime import date, timedelta

import pytest

from calmath import add_months, business_days_between


def test_add_months_clamping():
    assert add_months(2026, 1, 31, 1) == (2026, 2, 28)
    assert add_months(2024, 1, 31, 1) == (2024, 2, 29)   # 闰年
    assert add_months(2024, 2, 29, 12) == (2025, 2, 28)  # 闰日 + 12 月
    assert add_months(2026, 3, 31, -1) == (2026, 2, 28)
    assert add_months(2025, 12, 31, 2) == (2026, 2, 28)
    assert add_months(2026, 1, 31, 13) == (2027, 2, 28)


def test_add_months_normal():
    assert add_months(2026, 10, 3, 0) == (2026, 10, 3)
    assert add_months(2026, 1, 15, 11) == (2026, 12, 15)
    assert add_months(2026, 1, 15, 12) == (2027, 1, 15)
    assert add_months(2026, 6, 15, -6) == (2025, 12, 15)
    assert add_months(2026, 1, 31, -1) == (2025, 12, 31)


def brute_add_months(y, m, d, months):
    """独立 oracle:逐月步进(每次 ±1 个月,钳位)。"""
    step = 1 if months >= 0 else -1
    for _ in range(abs(months)):
        ny, nm = (y, m + step)
        if nm == 13:
            y, m = y + 1, 1
        elif nm == 0:
            y, m = y - 1, 12
        else:
            m = nm
        import calendar as _c

        d = min(d, _c.monthrange(y, m)[1])
    return y, m, d


def test_add_months_random_against_brute():
    random.seed(92)
    for _ in range(300):
        y = random.randint(1950, 2080)
        m = random.randint(1, 12)
        d = random.randint(1, 28)
        months = random.randint(-600, 600)
        assert add_months(y, m, d, months) == brute_add_months(y, m, d, months)


def brute_business(start, end, holidays):
    s = date(*start)
    e = date(*end)
    count = 0
    cur = s
    hol = {date(*h) for h in holidays}
    while cur < e:
        if cur.weekday() < 5 and cur not in hol:
            count += 1
        cur += timedelta(days=1)
    return count


def test_business_days_fixed():
    assert business_days_between((2026, 10, 1), (2026, 10, 1)) == 0
    assert business_days_between((2026, 10, 5), (2026, 10, 6)) == 1
    with pytest.raises(ValueError):
        business_days_between((2026, 10, 6), (2026, 10, 5))


def test_business_days_random_against_brute():
    random.seed(93)
    base = date(2026, 1, 4)
    for _ in range(80):
        a = random.randint(0, 400)
        b = a + random.randint(0, 60)
        s = base + timedelta(days=a)
        e = base + timedelta(days=b)
        hol = set()
        for _ in range(random.randint(0, 6)):
            h = base + timedelta(days=random.randint(0, 460))
            hol.add((h.year, h.month, h.day))
        assert business_days_between(
            (s.year, s.month, s.day), (e.year, e.month, e.day), frozenset(hol)
        ) == brute_business((s.year, s.month, s.day), (e.year, e.month, e.day), hol)


def test_weekend_holidays_not_double_subtracted():
    # 2026-10-03 是周六,2026-10-05 是周一
    sat = date(2026, 10, 3)
    mon = date(2026, 10, 5)
    assert sat.weekday() == 5 and mon.weekday() == 0
    span = ((2026, 10, 1), (2026, 10, 9))
    base = business_days_between(*span)
    with_weekend_hol = business_days_between(*span, frozenset({(2026, 10, 3)}))
    with_monday_hol = business_days_between(*span, frozenset({(2026, 10, 5)}))
    assert with_weekend_hol == base
    assert with_monday_hol == base - 1


def test_hundred_year_span_fast():
    import time

    holidays = frozenset(
        (y, 5, 1) for y in range(1926, 2027)
    )
    t0 = time.time()
    got = business_days_between((1926, 1, 1), (2026, 1, 1), holidays)
    dt = time.time() - t0
    assert dt < 2, f"太慢: {dt:.1f}s"
    assert got == brute_business((1926, 1, 1), (2026, 1, 1), holidays)
