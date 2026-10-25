"""ISO 8601 周日期换算。(mock 参考解)"""
from datetime import date, timedelta


def _ord(y, m, d):
    return date(y, m, d).toordinal()


def iso_week(year, month, day):
    d = date(year, month, day)  # 非法日期在此抛 ValueError
    o = d.toordinal()
    # 该日期所在周(以周一为起点)的序数
    monday = o - (d.weekday())
    # 找到这一周所属的 ISO 年:该周里至少 4 天所在的那一年 → 即包含周四的年
    thursday = monday + 3
    iso_year = date.fromordinal(thursday).year
    # iso_year 的第 1 周:包含其 1 月 4 日的那一周的周一
    jan4 = date(iso_year, 1, 4)
    week1_monday = jan4.toordinal() - jan4.weekday()
    week = (monday - week1_monday) // 7 + 1
    return (iso_year, week, d.weekday() + 1)
