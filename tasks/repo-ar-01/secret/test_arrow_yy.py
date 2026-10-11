from datetime import datetime

from arrow.parser import DateTimeParser


def p(s, fmt):
    return DateTimeParser().parse(s, fmt)


def test_posix_boundary():
    assert p('79-01-01 12:05:10', 'YY-MM-DD HH:mm:ss') == datetime(1979, 1, 1, 12, 5, 10)
    assert p('99-12-31 23:59:59', 'YY-MM-DD HH:mm:ss') == datetime(1999, 12, 31, 23, 59, 59)
    assert p('69-01-01 00:00:00', 'YY-MM-DD HH:mm:ss') == datetime(1969, 1, 1)


def test_below_boundary():
    assert p('68-01-01 00:00:00', 'YY-MM-DD HH:mm:ss') == datetime(2068, 1, 1)
    assert p('55-01-01 12:05:10', 'YY-MM-DD HH:mm:ss') == datetime(2055, 1, 1, 12, 5, 10)
    assert p('00-01-01 00:00:00', 'YY-MM-DD HH:mm:ss') == datetime(2000, 1, 1)


def test_four_digit_unchanged():
    assert p('2016-05-06', 'YYYY-MM-DD') == datetime(2016, 5, 6)
    assert p('1988-04-27 02:02:02', 'YYYY-MM-DD HH:mm:ss') == datetime(1988, 4, 27, 2, 2, 2)


def test_other_tokens_unaffected():
    assert p("Jan 24 2026", "MMM DD YYYY") == datetime(2026, 1, 24)
