import random
import time

from hull import convex_hull


def brute(pts):
    """独立 oracle:Jarvis 步进,严格凸包,共线取最远。"""
    pts = sorted(set(pts))
    if len(pts) <= 1:
        return list(pts)

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    # 全共线检测
    if all(cross(pts[0], pts[1], p) == 0 for p in pts[2:]):
        return [pts[0], pts[-1]]

    hull = []
    start = pts[0]
    cur = start
    while True:
        hull.append(cur)
        nxt = None
        for cand in pts:
            if cand == cur:
                continue
            if nxt is None:
                nxt = cand
                continue
            c = cross(cur, nxt, cand)
            if c < 0 or (c == 0 and (
                (cand[0] - cur[0]) ** 2 + (cand[1] - cur[1]) ** 2
                > (nxt[0] - cur[0]) ** 2 + (nxt[1] - cur[1]) ** 2
            )):
                nxt = cand
        cur = nxt
        if cur == start:
            break
    # Jarvis(选最右方向)产出为逆时针
    s = min(range(len(hull)), key=lambda i: hull[i])
    return hull[s:] + hull[:s]


def test_square_with_midpoints_excluded():
    pts = [(0, 0), (2, 0), (2, 2), (0, 2), (1, 0), (2, 1), (1, 2), (0, 1), (1, 1)]
    assert convex_hull(pts) == [(0, 0), (2, 0), (2, 2), (0, 2)]


def test_all_collinear():
    assert convex_hull([(0, 0), (1, 1), (2, 2), (5, 5), (3, 3)]) == [(0, 0), (5, 5)]
    assert convex_hull([(3, 3)]) == [(3, 3)]
    assert convex_hull([(3, 3), (3, 3), (3, 3)]) == [(3, 3)]


def test_two_points():
    assert convex_hull([(5, 5), (1, 1)]) == [(1, 1), (5, 5)]


def test_duplicates_do_not_appear():
    pts = [(0, 0)] * 10 + [(4, 0)] * 10 + [(0, 4)] + [(4, 4)]
    out = convex_hull(pts)
    assert out == [(0, 0), (4, 0), (4, 4), (0, 4)]


def test_interior_and_collinear_mixed():
    pts = [(0, 0), (4, 0), (4, 4), (0, 4), (2, 0), (2, 2), (1, 3), (2, 4)]
    assert convex_hull(pts) == [(0, 0), (4, 0), (4, 4), (0, 4)]


def test_random_against_brute():
    random.seed(71)
    for _ in range(80):
        n = random.randint(1, 40)
        pts = [
            (random.randint(-12, 12), random.randint(-12, 12)) for _ in range(n)
        ]
        assert convex_hull(pts) == brute(pts), pts


def test_collinear_heavy_random():
    random.seed(72)
    # 大量三点共线与重复点
    pts = []
    for _ in range(60):
        a, b = random.randint(-6, 6), random.randint(-6, 6)
        k = random.randint(0, 3)
        pts += [(a + k * i, b + k * i) for i in range(4)]
        pts += [(a, b)] * 2
    assert convex_hull(pts) == brute(pts)


def test_big_fast():
    import math

    rng = random.Random(73)
    pts = []
    # 1000 个圆周点(严格凸,全部在包上)
    for i in range(1000):
        ang = 2 * math.pi * i / 1000
        pts.append((round(10**9 * math.cos(ang)), round(10**9 * math.sin(ang))))
    # 30 万内部随机点
    pts += [(rng.randint(-10**8, 10**8), rng.randint(-10**8, 10**8)) for _ in range(300_000)]
    rng.shuffle(pts)
    t0 = time.time()
    out = convex_hull(pts)
    dt = time.time() - t0
    assert dt < 6, f"太慢: {dt:.1f}s,应 O(n log n)"
    assert len(out) >= 3
    # 抽查:输出严格左转(共线被剔除)
    n = len(out)
    for i in random.Random(74).sample(range(n), min(n, 60)):
        o, a, b = out[i], out[(i + 1) % n], out[(i + 2) % n]
        assert (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]) > 0
