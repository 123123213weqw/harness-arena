import random

import pytest

from cols import to_letters, to_num


def test_fixed_edges():
    assert to_num("A") == 1
    assert to_num("Z") == 26
    assert to_num("AA") == 27
    assert to_num("AZ") == 52
    assert to_num("BA") == 53
    assert to_num("ZZ") == 702
    assert to_num("AAA") == 703
    assert to_num("XFD") == 16384
    assert to_letters(1) == "A"
    assert to_letters(26) == "Z"
    assert to_letters(27) == "AA"
    assert to_letters(52) == "AZ"
    assert to_letters(53) == "BA"
    assert to_letters(702) == "ZZ"
    assert to_letters(703) == "AAA"
    assert to_letters(16384) == "XFD"


@pytest.mark.parametrize("bad", ["", "a", "Aa", "A1", " A", "A ", "A-B"])
def test_to_num_invalid(bad):
    with pytest.raises(ValueError):
        to_num(bad)


@pytest.mark.parametrize("n", [0, -1, 2**31, True])
def test_to_letters_invalid(n):
    with pytest.raises(ValueError):
        to_letters(n)


def test_roundtrip_random():
    random.seed(121)
    for _ in range(2000):
        n = random.randint(1, 2**31 - 1)
        assert to_num(to_letters(n)) == n
    for _ in range(2000):
        width = random.randint(1, 7)
        s = "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(width))
        try:
            n = to_num(s)
        except ValueError:  # 7 位大值可能超出 2^31-1,属合法拒绝
            continue
        assert to_letters(n) == s


def test_max_boundary():
    assert to_num(to_letters(2**31 - 1)) == 2**31 - 1
    assert to_letters(2**31 - 1) == "FXSHRXW"
