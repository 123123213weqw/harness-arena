"""算法练习:两数之和(返回数值对)。(mock 参考解)"""


def pair_sum(nums, target):
    n = len(nums)
    best = None
    for i in range(n):
        for j in range(i + 1, n):
            a, b = sorted((nums[i], nums[j]))
            if a + b == target and (best is None or (a, b) < best):
                best = (a, b)
    return best
