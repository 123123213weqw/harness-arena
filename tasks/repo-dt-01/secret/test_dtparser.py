import datetime as dt

import pytest

from dateutil.parser import parse


def test_normal_returns_datetime_not_tuple():
    out = parse("2026-01-02 03:04:05")
    assert out == dt.datetime(2026, 1, 2, 3, 4, 5)
    assert not isinstance(out, tuple)


def test_garbage_raises_valueerror():
    with pytest.raises(ValueError):
        parse("shouldfail")


def test_fuzzy_with_tokens_contract():
    out = parse("2026-01-02 hello world", fuzzy=True, fuzzy_with_tokens=True)
    assert isinstance(out, tuple) and len(out) == 2
    assert out[0] == dt.datetime(2026, 1, 2)
    assert "hello" in "".join(out[1])


def test_fuzzy_without_tokens_plain_datetime():
    out = parse("2026-01-02 extra words", fuzzy=True)
    assert out == dt.datetime(2026, 1, 2)
    assert not isinstance(out, tuple)


def test_default_parsing_unaffected():
    assert parse("Apr 10 2004 11:30", default=dt.datetime(2004, 1, 1)) == dt.datetime(2004, 4, 10, 11, 30)
