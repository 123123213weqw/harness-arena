"""INI 方言解析器。(mock 参考解:续行先按原文拼接,取值时统一转义)"""


def _unescape(v):
    out = []
    i = 0
    while i < len(v):
        if v[i] == "\\" and i + 1 < len(v) and v[i + 1] in ("n", "\\"):
            out.append("\n" if v[i + 1] == "n" else "\\")
            i += 2
        else:
            out.append(v[i])
            i += 1
    return "".join(out)


def parse(text):
    raw = {}
    cur = None
    last_key = None
    for line in text.split("\n"):
        line = line.rstrip("\r")
        if not line.strip():
            continue
        if line.startswith(";") or line.startswith("#"):
            continue
        if line.startswith(" "):  # 续行:去一个前导空格,单空格拼接
            if cur is None or last_key is None:
                raise ValueError(f"bad line: {line}")
            raw[cur][last_key] += " " + line[1:]
            continue
        if line.startswith("["):
            if not line.endswith("]") or len(line) < 3 or "]" in line[1:-1]:
                raise ValueError(f"bad line: {line}")
            cur = line[1:-1]
            raw.setdefault(cur, {})
            last_key = None
            continue
        key, eq, rest = line.partition("=")
        if (
            cur is None
            or not eq
            or not key.endswith(" ")
            or not rest.startswith(" ")
            or " " in key[:-1]
        ):
            raise ValueError(f"bad line: {line}")
        k = key[:-1]
        raw[cur][k] = rest[1:]
        last_key = k
    return {
        sec: {k: _unescape(v) for k, v in kv.items()} for sec, kv in raw.items()
    }
