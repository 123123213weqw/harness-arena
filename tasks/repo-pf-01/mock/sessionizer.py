"""访问日志会话化。(mock 参考解,O(n))"""


def sessionize(lines, gap_seconds=1800):
    sessions = {}
    cur = {}
    for ts, user in lines:
        s = cur.get(user)
        if s is not None and ts - s[1] <= gap_seconds:
            cur[user] = [s[0], ts, s[2] + 1]
        else:
            if s is not None:
                sessions.setdefault(user, []).append(tuple(s))
            cur[user] = [ts, ts, 1]
    for user, s in cur.items():
        sessions.setdefault(user, []).append(tuple(s))
    return sessions
