"""算法练习:逆序对计数。(mock 参考解)"""


def count_inversions(nums):
    def sort_count(a):
        n = len(a)
        if n <= 1:
            return a, 0
        mid = n // 2
        left, cl = sort_count(a[:mid])
        right, cr = sort_count(a[mid:])
        merged = []
        cnt = cl + cr
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                cnt += len(left) - i
                j += 1
        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged, cnt

    return sort_count(list(nums))[1]
