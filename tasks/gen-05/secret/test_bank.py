import random
from fractions import Fraction

import pytest

from bank import compound_interest_cents, valid_account


def oracle(cents, days, bp=100):
    f = Fraction(cents) * Fraction(10000 + bp, 10000) ** days
    return f.numerator // f.denominator  # floor


def test_known_error_case():
    assert compound_interest_cents(999, 3) == 1029  # 999 * 1.01^3 = 1029.27…
    assert compound_interest_cents(1, 2) == 1


def test_zero_days():
    assert compound_interest_cents(12345, 0) == 12345
    assert compound_interest_cents(0, 10) == 0


def test_random_against_fraction():
    random.seed(54)
    for _ in range(300):
        cents = random.randint(0, 10**6)
        days = random.randint(0, 30)
        bp = random.randint(1, 500)
        assert compound_interest_cents(cents, days, bp) == oracle(cents, days, bp)


@pytest.mark.parametrize(
    "code,ok",
    [
        ("ACC-123456", True),
        ("ACC-000000", True),
        ("ACC-12345", False),
        ("ACC-1234567", False),
        ("XACC-123456", False),
        ("ACC-123456X", False),
        ("acc-123456", False),
        ("ACC-12a456", False),
        ("ACC_123456", False),
        ("ACC-", False),
        ("", False),
    ],
)
def test_valid_account(code, ok):
    assert valid_account(code) is ok
