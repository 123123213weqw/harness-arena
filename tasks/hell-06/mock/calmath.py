"""日历算术。(mock 参考解)"""
import calendar
from datetime import date


def add_months(year, month, day, months):
    total = year * 12 + (month - 1) + months
    y, m0 = divmod(total, 12)
    m = m0 + 1
    last = calendar.monthrange(y, m)[1]
    return y, m, min(day, last)


def business_days_between(start, end, holidays=frozenset()):
    s = date(*start)
    e = date(*end)
    if s > e:
        raise ValueError("start 晚于 end")
    days = (e - s).days
    full_weeks, rem = divmod(days, 7)
    count = full_weeks * 5
    wd = s.weekday()
    for i in range(rem):
        if (wd + i) % 7 < 5:
            count += 1
    for h in holidays:
        dh = date(*h)
        if s <= dh < e and dh.weekday() < 5:
            count -= 1
    return count
