import pytest

from interp import run


def test_factorial():
    assert run([
        "n = 5", "r = 1", "i = 1",
        "while i <= n: r = r * i; i = i + 1",
        "print r",
    ]) == ["120"]


def test_fibonacci():
    assert run([
        "a = 0", "b = 1", "i = 0",
        "while i < 10: t = a + b; a = b; b = t; i = i + 1",
        "print a",
    ]) == ["55"]


def test_precedence():
    assert run(["print 2 + 3 * 4 - 10 / 3"]) == ["11"]
    assert run(["print (2 + 3) * (4 - 1)"]) == ["15"]


def test_floor_div_semantics():
    assert run(["print -7 / 2", "print -7 % 3", "print 7 / -2"]) == ["-4", "2", "-4"]


def test_comparisons_and_non_chaining():
    assert run(["print 3 < 5", "print 2 == 2", "print 2 <= 1"]) == ["1", "1", "0"]
    # 非链式比较:((1<2) == 1) == 1(Python 链式语义会是 0)
    assert run(["print 1 < 2 == 1"]) == ["1"]


def test_if_body():
    assert run(["x = 7", "if x % 2 == 1: print 99; print x % 2", "print x"]) == ["99", "1", "7"]


def test_if_false_skips_body():
    assert run(["if 0: print 1; print 2", "print 3"]) == ["3"]


def test_while_loop_sum():
    assert run([
        "s = 0", "i = 1",
        "while i <= 100: s = s + i; i = i + 1",
        "print s",
    ]) == ["5050"]


def test_while_false_never():
    assert run(["while 0: print 1", "print 2"]) == ["2"]


def test_unary():
    assert run(["print -3 + -4", "print --5"]) == ["-7", "5"]


def test_reassignment():
    assert run(["x = 3", "x = x * x", "x = x * x", "print x"]) == ["81"]


def test_big_integers():
    assert run(["print 2 * 1000000007 * 999999937"]) == ["1999999887999999118"]


def test_empty_program():
    assert run([]) == []


def test_undefined_variable_raises():
    with pytest.raises(ValueError):
        run(["print 1", "print y"])


def test_division_by_zero_raises():
    with pytest.raises(ValueError):
        run(["x = 0", "print 5 / x"])


def test_syntax_error_raises():
    with pytest.raises(ValueError):
        run(["print 2 +"])


def test_nested_control_rejected():
    with pytest.raises(ValueError):
        run(["while 1: if 2: print 3"])


def test_step_limit():
    with pytest.raises(RuntimeError):
        run(["i = 0", "while 1: i = i + 1"])
