"""Sprague-Grundy:石堆拆分博弈。(mock 参考解)"""


def winner(piles):
    m = max(piles) if piles else 0
    g = [0] * (m + 1)
    for n in range(1, m + 1):
        seen = set()
        for a in range(1, n):
            b = n - a
            if a == b:
                continue
            seen.add(g[a] ^ g[b])
        mex = 0
        while mex in seen:
            mex += 1
        g[n] = mex
    x = 0
    for p in piles:
        x ^= g[p]
    return "First" if x else "Second"
