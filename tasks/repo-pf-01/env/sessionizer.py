"""访问日志会话化(O(n²) 实现,行为正确但太慢)。"""


def sessionize(lines, gap_seconds=1800):
    """lines: 升序 (ts, user) 列表 → {user: [(start, end, count), ...]}"""
    sessions = {}
    for ts, user in lines:
        lst = sessions.setdefault(user, [])
        for s in lst:
            if ts - s[1] <= gap_seconds:
                s[1] = ts
                s[2] += 1
                break
        else:
            lst.append([ts, ts, 1])
    return {u: [tuple(s) for s in lst] for u, lst in sessions.items()}
