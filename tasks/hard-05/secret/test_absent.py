import random
import time
from itertools import product

from absent import smallest_absent


def brute(s):
    subs = {s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1)}
    for L in range(1, 8):
        for tup in product("abcdefghijklmnopqrstuvwxyz", repeat=L):
            cand = "".join(tup)
            if cand not in subs:
                return cand
    raise AssertionError


def test_fixed():
    assert smallest_absent("a") == "b"
    assert smallest_absent("b") == "a"
    assert smallest_absent("ab") == "c"
    assert smallest_absent("aaa") == "b"
    assert smallest_absent("abcdefghijklmnopqrstuvwxyz") == "aa"
    assert smallest_absent("zyxwvutsrqponmlkjihgfedcba") == "aa"
    assert smallest_absent("abab") == "c"


def test_random_against_brute():
    random.seed(39)
    for _ in range(150):
        s = "".join(random.choice("abc") for _ in range(random.randint(1, 30)))
        assert smallest_absent(s) == brute(s), s
    for _ in range(40):
        s = "".join(random.choice("ab") for _ in range(random.randint(1, 15)))
        assert smallest_absent(s) == brute(s), s


def test_full_but_dense():
    s = "abcdefghijklmnopqrstuvwxyz" * 8000  # 20.8 万长,含全部单字母
    got = smallest_absent(s)
    assert len(got) <= 4
    # 抽查:答案确实不在 s 里
    assert got not in s


def test_big_fast():
    random.seed(40)
    s = "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(200_000))
    t0 = time.time()
    got = smallest_absent(s)
    dt = time.time() - t0
    assert dt < 3, f"太慢: {dt:.1f}s"
    assert len(got) <= 4
    # 抽查:答案确实不在 s 里
    assert got not in s
