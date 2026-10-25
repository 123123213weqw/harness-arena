import pytest

from more_itertools import one, only


class FalsyError(Exception):
    def __bool__(self):
        return False


def test_one_too_long_falsy_custom():
    with pytest.raises(FalsyError):
        one([1, 2, 3], too_long=FalsyError("boom"))


def test_one_too_short_falsy_custom():
    with pytest.raises(FalsyError):
        one([], too_short=FalsyError("empty"))


def test_only_too_long_falsy_custom():
    with pytest.raises(FalsyError):
        only([1, 2, 3], too_long=FalsyError("boom"))


def test_truthy_custom_still_works():
    with pytest.raises(KeyError):
        one([1, 2], too_long=KeyError("k"))
    with pytest.raises(KeyError):
        one([], too_short=KeyError("s"))
    with pytest.raises(ValueError, match="perhaps more"):
        only([1, 2, 3])


def test_default_valueerror_kept():
    with pytest.raises(ValueError, match="too few items"):
        one([])
    with pytest.raises(ValueError, match="perhaps more"):
        one([1, 2, 3])
    with pytest.raises(ValueError, match="perhaps more"):
        only([1, 2])
    assert only([]) is None
    assert only([], default=42) == 42


def test_one_happy_paths():
    assert one([9]) == 9
    assert only([7]) == 7
    with pytest.raises(ValueError):
        one([])
