"""字典序最小的最短缺失子串。(mock 参考解)"""
from itertools import product

_ALPHABET = "abcdefghijklmnopqrstuvwxyz"


def smallest_absent(s):
    n = len(s)
    for L in range(1, 7):
        present = {s[i : i + L] for i in range(n - L + 1)}
        if len(present) == 26**L:
            continue
        for tup in product(_ALPHABET, repeat=L):
            cand = "".join(tup)
            if cand not in present:
                return cand
    raise AssertionError("unreachable for |s| ≤ 2e5")
