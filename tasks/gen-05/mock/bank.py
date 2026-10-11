"""银行小工具。(mock 参考解)"""
import re

_ACC = re.compile(r"^ACC-[0-9]{6}$")


def compound_interest_cents(cents, days, daily_rate_bp=100):
    num = cents * (10000 + daily_rate_bp) ** days
    return num // 10000**days


def valid_account(code):
    return bool(_ACC.match(code))
