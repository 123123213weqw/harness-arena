"""巨型组合数取模。(mock 参考解)"""


def comb_mod(n, r, mod=998244353):
    if r < 0 or r > n:
        return 0
    r = min(r, n - r)
    num = 1
    for i in range(r):
        num = num * ((n - i) % mod) % mod
    den = 1
    for i in range(2, r + 1):
        den = den * i % mod
    return num * pow(den, mod - 2, mod) % mod
