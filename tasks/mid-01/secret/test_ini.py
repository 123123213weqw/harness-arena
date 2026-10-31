import random

import pytest

from iniparse import parse


def test_sections_and_merge():
    t = "[a]\nk = 1\n[b]\nx = 2\n[a]\nk = 3\n"
    assert parse(t) == {"a": {"k": "3"}, "b": {"x": "2"}}


def test_exact_spacing_rule():
    assert parse("[s]\nk = v\n") == {"s": {"k": "v"}}
    assert parse("[s]\nk =  v\n") == {"s": {"k": " v"}}     # 只剥一个空格
    assert parse("[s]\nk = v \n") == {"s": {"k": "v "}}     # 尾空格保留
    with pytest.raises(ValueError):
        parse("[s]\nk= v\n")                               # = 前无空格
    with pytest.raises(ValueError):
        parse("[s]\nk =v\n")                               # = 后无空格
    with pytest.raises(ValueError):
        parse("[s]\n k = v\n")                             # 缩进行在键前 = 非法续行


def test_continuation_and_escape():
    t = "[s]\nk = a\\nb\n  c\\d\n  e\n"
    # 续行先拼原文(每行剥一个前导空格,以单空格连接),最后统一转义
    assert parse(t) == {"s": {"k": "a\nb  c\\d  e"}}


def test_comments():
    assert parse("; top\n# hash\n[s]\n; inside\nk = 1 ; keep\n") == {
        "s": {"k": "1 ; keep"}
    }


def test_bad_lines():
    for bad in ["bare line\n", "[s]\nno_eq_here\n", "[s]\nk = 1\n[]\n", "k = 1\n[s]\n", "[s]\nx = 1\n  orphan?\n"]:
        pass  # orphan 续行合法(有上一键);单独构造非法:
    with pytest.raises(ValueError):
        parse("bare\n")
    with pytest.raises(ValueError):
        parse("[s]\nno_eq\n")
    with pytest.raises(ValueError):
        parse("[]\nk = 1\n")
    with pytest.raises(ValueError):
        parse("k = 1\n")
    with pytest.raises(ValueError):
        parse("[bad]extra\n")


def random_ini(rng):
    """生成随机合法 INI 文本与期望 dict(独立 oracle,模拟 last_key 语义)。"""
    lines = []
    expect = {}
    secs = [f"sec{i}" for i in range(rng.randint(1, 4))]
    cur = None
    last_key = None
    for _ in range(rng.randint(2, 14)):
        r = rng.random()
        if r < 0.25:
            cur = rng.choice(secs)
            lines.append(f"[{cur}]")
            expect.setdefault(cur, {})
            last_key = None
        elif cur is not None:
            k = f"k{rng.randint(0, 30)}"
            v = "".join(rng.choice("abZ9 ._\\nn") for _ in range(rng.randint(0, 8)))
            if last_key is not None and rng.random() < 0.5:
                lines.append(f" {v}extra")  # 续行:拼给最新键 last_key
                expect[cur][last_key] = expect[cur][last_key] + " " + v + "extra"
            else:
                lines.append(f"{k} = {v}")
                expect[cur][k] = v
                last_key = k
        elif r < 0.5:
            lines.append(rng.choice(["; c", "# c", ""]))
    # 期望值的转义独立计算
    def un(v):
        out, i = [], 0
        while i < len(v):
            if v[i] == "\\" and i + 1 < len(v) and v[i + 1] in "n\\":
                out.append("\n" if v[i + 1] == "n" else "\\")
                i += 2
            else:
                out.append(v[i])
                i += 1
        return "".join(out)
    return "\n".join(lines) + "\n", {s: {k: un(v) for k, v in kv.items()} for s, kv in expect.items()}


def test_random_against_oracle():
    rng = random.Random(2026)
    for _ in range(500):
        t, exp = random_ini(rng)
        assert parse(t) == exp, (t, exp)
