"""Excel 列名列号互转。(mock 参考解)"""

_MAX = 2**31 - 1


def to_num(letters):
    if not isinstance(letters, str) or not letters or not letters.isascii():
        raise ValueError("非法列名")
    n = 0
    for ch in letters:
        v = ord(ch) - 64
        if not 1 <= v <= 26:
            raise ValueError("非法列名")
        n = n * 26 + v
    if n > _MAX:
        raise ValueError("超出范围")
    return n


def to_letters(n):
    if not isinstance(n, int) or isinstance(n, bool) or not 1 <= n <= _MAX:
        raise ValueError("非法列号")
    out = []
    while n:
        n, r = divmod(n - 1, 26)
        out.append(chr(65 + r))
    return "".join(reversed(out))
