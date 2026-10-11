import stats


def test_odd():
    assert stats.median([3, 1, 2]) == 2


def test_even():
    assert stats.median([1, 2, 3, 4]) == 2.5


def test_even_float():
    assert stats.median([10, 20]) == 15.0


def test_single():
    assert stats.median([7]) == 7


def test_unsorted_even():
    assert stats.median([9, -1, 5, 3]) == 4.0


def test_p95_untouched():
    assert abs(stats.p95(list(range(1, 101))) - 95.05) < 1e-9
