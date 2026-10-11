"""算法练习:滑动窗口最大值。(mock 参考解)"""
from collections import deque


def sliding_max(nums, k):
    n = len(nums)
    if k <= 0 or k > n:
        raise ValueError("k 非法")
    dq = deque()  # 存下标,对应值单调递减
    out = []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out
