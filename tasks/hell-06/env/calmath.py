"""日历算术(月末钳位 + 工作日计数)。"""


def add_months(year, month, day, months):
    """平移 months 个月,日号钳位到目标月末;返回 (y, m, d)。"""
    raise NotImplementedError


def business_days_between(start, end, holidays=frozenset()):
    """[start, end) 内工作日数(扣除节假日中的工作日);start > end 抛 ValueError。"""
    raise NotImplementedError
