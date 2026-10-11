import csv
import random

import pytest

from csvmini import split_line


def oracle(line):
    return next(csv.reader([line.rstrip("\r\n")]))


def test_quoted_comma():
    assert split_line('a,"b,c",d') == ["a", "b,c", "d"]


def test_escaped_quotes():
    assert split_line('"say ""hi"""') == ['say "hi"']
    assert split_line('"a""b",c') == ['a"b', "c"]


def test_trailing_newline():
    assert split_line("x,y\n") == ["x", "y"]
    assert split_line("x,y\r\n") == ["x", "y"]


def test_empty_and_blanks():
    assert split_line("") == [""]
    assert split_line(",") == ["", ""]
    assert split_line("a,,c") == ["a", "", "c"]


def test_unclosed_quote_raises():
    with pytest.raises(ValueError):
        split_line('"abc')


def _encode_field(f):
    if "," in f or '"' in f:
        return '"' + f.replace('"', '""') + '"'
    return f


def test_random_against_csv_module():
    random.seed(4)
    for _ in range(600):
        n = random.randint(1, 6)
        raws = [
            "".join(
                random.choice("ab, ") for _ in range(random.randint(0, 6))
            )
            for _ in range(n)
        ]
        line = ",".join(_encode_field(f) for f in raws)
        if line == "":  # 完全空行与 csv 模块语义不同(规范定为 ['']),专测已覆盖
            continue
        if random.random() < 0.3:
            line += random.choice(["\n", "\r\n"])
        assert split_line(line) == raws == oracle(line), line
