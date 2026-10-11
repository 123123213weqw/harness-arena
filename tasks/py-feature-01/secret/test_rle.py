import random

import pytest

from rle import rle_decode, rle_encode


def test_encode_fixed():
    assert rle_encode("aaabbc") == "a3b2c1"
    assert rle_encode("") == ""
    assert rle_encode("a") == "a1"
    assert rle_encode("abcdefgh") == "a1b1c1d1e1f1g1h1"


def test_decode_fixed():
    assert rle_decode("a3b2c1") == "aaabbc"
    assert rle_decode("") == ""
    assert rle_decode("a10") == "aaaaaaaaaa"


def test_roundtrip_random():
    random.seed(11)
    for _ in range(300):
        s = "".join(random.choice("ab") for _ in range(random.randint(0, 60)))
        assert rle_decode(rle_encode(s)) == s


@pytest.mark.parametrize("bad", ["3a", "a", "a0", "a01", "A3", "a3b", "3", "a 3"])
def test_decode_invalid(bad):
    with pytest.raises(ValueError):
        rle_decode(bad)
