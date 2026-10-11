"""最近点对。(mock 参考解,分治 O(n log n))"""
import sys


def closest_pair_sq(points):
    n = len(points)
    if n < 2:
        raise ValueError("至少需要两个点")
    pts = sorted(points)
    sys.setrecursionlimit(max(10000, 2 * n))

    def d2(a, b):
        return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

    best = [float("inf")]

    def rec(lo, hi):
        if hi - lo <= 3:
            for i in range(lo, hi):
                for j in range(i + 1, hi):
                    d = d2(pts[i], pts[j])
                    if d < best[0]:
                        best[0] = d
            return
        mid = (lo + hi) // 2
        xm = pts[mid][0]
        rec(lo, mid)
        rec(mid, hi)
        strip = [p for p in pts[lo:hi] if (p[0] - xm) ** 2 < best[0]]
        strip.sort(key=lambda p: p[1])
        m = len(strip)
        for i in range(m):
            for j in range(i + 1, min(i + 8, m)):
                d = d2(strip[i], strip[j])
                if d < best[0]:
                    best[0] = d

    rec(0, n)
    return best[0]
