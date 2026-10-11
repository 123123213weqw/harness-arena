"""严格凸包。(mock 参考解,Andrew 单调链)"""


def convex_hull(points):
    pts = sorted(set((x, y) for x, y in points))
    if len(pts) <= 1:
        return list(pts)

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    # 单调链天然以字典序最小点起始、逆时针;全部共线时恰为 [min, max]
    return lower[:-1] + upper[:-1]
