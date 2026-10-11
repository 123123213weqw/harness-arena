"""银行小工具(带 bug)。"""


def compound_interest_cents(cents, days, daily_rate_bp=100):
    """按日复利:每天乘 (10000+daily_rate_bp)/10000,最后向下取整为分,返回 int。"""
    for _ in range(days):
        cents = cents + cents * daily_rate_bp // 10000
    return cents


def valid_account(code):
    """合法账号:恰好 'ACC-' + 6 位数字。"""
    return "ACC-" in code and len(code) > 4
