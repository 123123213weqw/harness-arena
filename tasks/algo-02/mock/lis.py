"""算法练习:最长严格递增子序列长度。(mock 参考解)"""
from bisect import bisect_left


def lis_length(nums):
    tails = []
    for x in nums:
        i = bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)
