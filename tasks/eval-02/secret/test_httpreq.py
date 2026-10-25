import random

import pytest

from httpreq import parse_request


def req(line, headers=(), body=b""):
    head = "\r\n".join([line] + list(headers)) + "\r\n\r\n"
    return head.encode("latin-1") + body


def test_minimal():
    r = parse_request(req("GET / HTTP/1.1"))
    assert r == {"method": "GET", "target": "/", "version": "HTTP/1.1", "headers": {}}


def test_headers_case_and_ows():
    r = parse_request(req(
        "POST /api/x HTTP/1.0",
        ["Host:  example.com ", "Content-Type:\ttext/plain"],
    ))
    assert r["method"] == "POST"
    assert r["version"] == "HTTP/1.0"
    assert r["headers"] == {"host": "example.com", "content-type": "text/plain"}


def test_duplicate_headers_joined():
    r = parse_request(req("GET / HTTP/1.1", [
        "Set-Cookie: a=1", "X-Multi: first", "set-cookie: b=2", "X-Multi: second",
    ]))
    assert r["headers"]["set-cookie"] == "a=1, b=2"
    assert r["headers"]["x-multi"] == "first, second"


def test_body_ignored():
    r = parse_request(req("GET / HTTP/1.1", ["Host: x"], body=b"whatever\r\nmore"))
    assert r["headers"] == {"host": "x"}


def test_no_terminator_rejected():
    with pytest.raises(ValueError, match="incomplete"):
        parse_request(b"GET / HTTP/1.1\r\nHost: x\r\n")


@pytest.mark.parametrize("bad", [
    "GET  /  HTTP/1.1",          # 双空格
    "GET\t/ HTTP/1.1",           # tab 分隔
    "GET / HTTP/2.0",            # 版本
    "GET / HTTP/11",             # 版本
    "get / HTTP/1.1",            # 小写方法
    "GET /",                     # 两段
    "GET / HTTP/1.1 extra",      # 四段
])
def test_bad_request_line(bad):
    with pytest.raises(ValueError):
        parse_request(req(bad))


@pytest.mark.parametrize("bad", [
    " Bad-Fold: x",              # obs-fold
    "\tBad-Fold: x",
    ": novalue",                 # 空头名
    "Bad Header: x",             # 名含空格
])
def test_bad_headers(bad):
    with pytest.raises(ValueError):
        parse_request(req("GET / HTTP/1.1", [bad]))


def test_colon_in_value_is_legal():
    # 头部值可以含冒号:第一个冒号是分隔符,其后整体为值
    r = parse_request(req("GET / HTTP/1.1", ["Referer: http://example.com:8080/x"]))
    assert r["headers"]["referer"] == "http://example.com:8080/x"


def test_empty_header_value_allowed():
    r = parse_request(req("GET / HTTP/1.1", ["X-Empty:"]))
    assert r["headers"]["x-empty"] == ""


def test_internal_whitespace_preserved():
    r = parse_request(req("GET / HTTP/1.1", ["X-Two: a  b\tc "]))
    assert r["headers"]["x-two"] == "a  b\tc"


def test_random_wellformed_roundtrip():
    random.seed(101)
    names = ["X-A", "x-a", "Host", "Accept", "ACCEPT"]
    for _ in range(300):
        n = random.randint(0, 5)
        pairs = []
        for _ in range(n):
            k = random.choice(names)
            v = "".join(random.choice("ab7 .") for _ in range(random.randint(0, 8))).strip()
            pairs.append((k, v))
        line = random.choice(["GET /x HTTP/1.1", "POST /y?q=1 HTTP/1.0"])
        raw = req(line, [f"{k}: {v}" for k, v in pairs])
        r = parse_request(raw)
        assert r["method"] == line.split()[0]
        joined = {}
        for k, v in pairs:
            joined[k.lower()] = v if k.lower() not in joined else joined[k.lower()] + ", " + v
        assert r["headers"] == joined
