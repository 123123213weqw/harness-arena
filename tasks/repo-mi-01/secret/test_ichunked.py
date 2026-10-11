import pytest

from more_itertools import ichunked


def test_normal_unchanged():
    assert [list(c) for c in ichunked([1, 2, 3, 4, 5], 2)] == [[1, 2], [3, 4], [5]]
    assert [list(c) for c in ichunked([], 3)] == []
    assert [list(c) for c in ichunked([1], 1)] == [[1]]


def test_out_of_order():
    x = [1, 2, 3, 4, 5, 6, 7]
    actual = [list(c) for c in ichunked(iter(x), 3)]
    assert actual == [[1, 2, 3], [4, 5, 6], [7]]


def test_zero():
    assert [list(c) for c in ichunked([], 0)] == []
    assert [list(c) for c in ichunked([1, 2, 3], 0)] == []


def test_zero_does_not_consume_source():
    source = iter([1, 2, 3])
    assert [list(c) for c in ichunked(source, 0)] == []
    assert list(source) == [1, 2, 3]


def test_negative():
    with pytest.raises(ValueError) as cm:
        [list(c) for c in ichunked(iter([1]), -1)]
    assert "n must be at least 0" in str(cm.value)
