"""统计小工具库。(mock 参考解)"""


def median(nums):
    """返回中位数。

    奇数个元素返回中间元素;偶数个元素返回中间两个元素的平均值,
    例如 median([1, 2, 3, 4]) == 2.5。
    """
    s = sorted(nums)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2


def p95(nums):
    """返回第 95 百分位数(线性插值,与 numpy.percentile 默认一致)。"""
    s = sorted(nums)
    k = 0.95 * (len(s) - 1)
    f = int(k)
    c = min(f + 1, len(s) - 1)
    return s[f] + (s[c] - s[f]) * (k - f)
