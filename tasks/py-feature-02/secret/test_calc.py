import random

import pytest

from calc import evaluate


def test_fixed():
    assert evaluate("1+2*3") == 7
    assert evaluate("(1+2)*3") == 9
    assert evaluate("2-3-4") == -5
    assert evaluate("2-(3-4)") == 3
    assert evaluate("12*-3") == -36
    assert evaluate("3--2") == 5
    assert evaluate("-7//2") == -4
    assert evaluate("-7%3") == 2
    assert evaluate(" 1 + 2 ") == 3
    assert evaluate("((2))") == 2
    assert evaluate("100") == 100


@pytest.mark.parametrize(
    "bad",
    ["", "2+", "*3", "(1+2", "1+2)", "1 2", "1..2", "+", "()", "a+1", "1+()"],
)
def test_invalid(bad):
    with pytest.raises(ValueError):
        evaluate(bad)


def _rand_expr(depth=0):
    if depth > 3 or random.random() < 0.35:
        return str(random.randint(0, 99))
    a = _rand_expr(depth + 1)
    b = _rand_expr(depth + 1)
    op = random.choice(["+", "-", "*", "//", "%"])
    if op in ("//", "%"):  # 避免除零:右侧用正整数字面量
        b = str(random.randint(1, 9))
    e = f"{a}{op}{b}"
    if random.random() < 0.3:
        e = f"({e})"
    if random.random() < 0.1:
        e = f"-{e}"
    return e


def test_random_against_eval():
    random.seed(42)
    for _ in range(1000):
        e = _rand_expr()
        assert evaluate(e) == eval(e), e
