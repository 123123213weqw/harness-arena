import pytest

from more_itertools import constrained_batches


def test_doc_example_unchanged():
    iterable = [b"12345", b"123", b"12345678", b"1", b"1", b"12", b"1"]
    assert list(constrained_batches(iterable, 10)) == [
        (b"12345", b"123"),
        (b"12345678", b"1", b"1"),
        (b"12", b"1"),
    ]


def test_max_count_two():
    iterable = ["1", "12345678", "1", "12345", "12345"]
    actual = list(constrained_batches(iterable, 8, max_count=2))
    assert actual == [("1",), ("12345678",), ("1", "12345"), ("12345",)]


def test_max_count_one():
    assert list(constrained_batches(["", "a", ""], 10, max_count=1)) == [
        ("",),
        ("a",),
        ("",),
    ]


def test_nonpositive_max_count():
    for mc in (0, -1):
        for items in ([], ["a", "b"]):
            source = iter(items)
            with pytest.raises(ValueError, match="maximum count must be greater than zero"):
                list(constrained_batches(source, 10, mc))
            assert list(source) == items


def test_max_size_validation_unchanged():
    with pytest.raises(ValueError, match="maximum size must be greater than zero"):
        list(constrained_batches(["a"], 0))
