import datetime as dt
from pathlib import Path

import pytest

from calweek import iso_week


def test_no_isocalendar_call():
    src = Path("calweek.py").read_text(encoding="utf-8")
    assert "isocalendar" not in src, "不得调用 isocalendar"


def test_boundary_dates():
    assert iso_week(2021, 1, 1) == (2020, 53, 5)
    assert iso_week(2024, 12, 30) == (2025, 1, 1)
    assert iso_week(2026, 1, 1) == (2026, 1, 4)
    assert iso_week(2016, 1, 3) == (2015, 53, 7)
    assert iso_week(2019, 12, 30) == (2020, 1, 1)
    assert iso_week(2004, 1, 1) == (2004, 1, 4)
    assert iso_week(2005, 1, 1) == (2004, 53, 6)
    assert iso_week(2005, 1, 2) == (2004, 53, 7)
    assert iso_week(2005, 1, 3) == (2005, 1, 1)
    assert iso_week(2026, 12, 28) == (2026, 53, 1)
    assert iso_week(2027, 1, 4) == (2027, 1, 1)


@pytest.mark.parametrize("bad", [(2026, 2, 30), (2026, 13, 1), (2026, 0, 5), (2026, 1, 0), (0, 1, 1), (10000, 1, 1)])
def test_invalid_dates(bad):
    with pytest.raises(ValueError):
        iso_week(*bad)


def test_exhaustive_against_stdlib():
    d = dt.date(1900, 1, 1)
    end = dt.date(2100, 12, 31)
    one = dt.timedelta(days=1)
    n = 0
    while d <= end:
        assert iso_week(d.year, d.month, d.day) == d.isocalendar()[:3], d
        d += one
        n += 1
    assert n == (end.toordinal() - dt.date(1900, 1, 1).toordinal() + 1)  # 防假跑
