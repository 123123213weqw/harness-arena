"""数位 DP 计数。(mock 参考解)"""
from functools import lru_cache


def count_beacons(N, k):
    s = str(N)
    n = len(s)

    @lru_cache(maxsize=None)
    def f(i, sm, tight, prev, started):
        if i == n:
            return 1 if (started and sm % k == 0) else 0
        hi = int(s[i]) if tight else 9
        total = 0
        for d in range(hi + 1):
            if prev == 1 and d == 3:  # 出现 "13"
                continue
            total += f(
                i + 1,
                (sm + d) % k,
                tight and d == hi,
                d if (started or d > 0) else -1,
                started or d > 0,
            )
        return total

    return f(0, 0, True, -1, False)
