"""算法练习:最大连续子数组和。(mock 参考解)"""


def max_subarray_sum(nums):
    """返回非空整数列表 nums 的最大连续子数组和,要求 O(n)。

    全为负数时返回最大元素。
    """
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best
