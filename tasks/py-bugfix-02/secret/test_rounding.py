from rounding import my_round


def test_half_even_unit():
    assert my_round(2.5) == 2
    assert my_round(3.5) == 4
    assert my_round(-2.5) == -2


def test_decimals():
    assert my_round(0.125, 2) == 0.12
    assert my_round(0.135, 2) == 0.14
    assert my_round(2.675, 2) == 2.68


def test_normal_cases():
    assert my_round(2.4) == 2
    assert my_round(2.6) == 3


def test_negative_ndigits():
    assert my_round(1234.5, -2) == 1200
    assert my_round(126, -1) == 130


def test_roundtrip_types():
    assert isinstance(my_round(2.5), float)
