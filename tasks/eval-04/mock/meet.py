"""多人共同空闲时段。(mock 参考解)"""


def common_free(busy_by_person, window, min_len):
    ws, we = window
    if ws >= we:
        raise ValueError("空窗口")
    if min_len <= 0:
        raise ValueError("min_len 必须为正")

    clipped = []
    for person in busy_by_person:
        for s, e in person:
            s2, e2 = max(s, ws), min(e, we)
            if s2 < e2:
                clipped.append((s2, e2))
    clipped.sort()

    merged = []
    for s, e in clipped:
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])

    out = []
    prev_end = ws
    for s, e in merged:
        if s - prev_end >= min_len:
            out.append((prev_end, s))
        prev_end = max(prev_end, e)
    if we - prev_end >= min_len:
        out.append((prev_end, we))
    return out
