"""游程编码工具。(mock 参考解)"""
import re
from itertools import groupby

_ENC_RE = re.compile(r"([a-z])([1-9][0-9]*)")


def rle_encode(s):
    return "".join(f"{ch}{sum(1 for _ in g)}" for ch, g in groupby(s))


def rle_decode(s):
    if not re.fullmatch(r"(?:[a-z][1-9][0-9]*)*", s):
        raise ValueError(f"invalid RLE input: {s!r}")
    return "".join(ch * int(n) for ch, n in _ENC_RE.findall(s))
