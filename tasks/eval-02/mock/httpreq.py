"""HTTP/1.x 请求首部解析。(mock 参考解)"""
import re

_NAME = re.compile(r"^[!-9;-~]+$")  # token 字符,排除 ':'(58)


def parse_request(data: bytes) -> dict:
    text = data.decode("latin-1")
    idx = text.find("\r\n\r\n")
    if idx == -1:
        raise ValueError("incomplete")
    head = text[:idx]
    lines = head.split("\r\n")
    req_line = lines[0]
    if "\t" in req_line or "  " in req_line:
        raise ValueError("malformed request line")
    parts = req_line.split(" ")
    if len(parts) != 3:
        raise ValueError("malformed request line")
    method, target, version = parts
    if not method or not method.isascii() or not method.isupper() or not method.isalpha():
        raise ValueError("bad method")
    if " " in target or "\t" in target:
        raise ValueError("bad target")
    if version not in ("HTTP/1.0", "HTTP/1.1"):
        raise ValueError("bad version")

    headers: dict[str, list[str]] = {}
    for line in lines[1:]:
        if not line:
            continue
        if line[0] in (" ", "\t"):
            raise ValueError("obs-fold")
        name, sep, value = line.partition(":")
        if not sep:
            raise ValueError("malformed header")
        if not name or not _NAME.match(name) or " " in name or "\t" in name:
            raise ValueError("bad header name")
        headers.setdefault(name.lower(), []).append(value.strip(" \t"))

    return {
        "method": method,
        "target": target,
        "version": version,
        "headers": {k: ", ".join(v) for k, v in headers.items()},
    }
