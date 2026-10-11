"""带权区间调度。(mock 参考解)"""
from bisect import bisect_right


def max_value(intervals):
    if not intervals:
        return 0
    ivs = sorted(intervals, key=lambda x: x[1])
    ends = [e for _s, e, _v in ivs]
    dp = [0] * (len(ivs) + 1)
    for i, (s, _e, v) in enumerate(ivs, 1):
        j = bisect_right(ends, s, 0, i - 1)
        dp[i] = max(dp[i - 1], dp[j] + v)
    return dp[len(ivs)]
