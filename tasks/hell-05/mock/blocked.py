"""取消链路与环检测。(mock 参考解)"""


def blocked_jobs(jobs, cancelled):
    by_id = {j.id: j for j in jobs}
    dependents = {}
    for j in jobs:
        for d in j.deps:
            dependents.setdefault(d, set()).add(j.id)

    blocked = set()
    stack = [c for c in cancelled]
    while stack:
        cur = stack.pop()
        if cur in blocked:
            continue
        blocked.add(cur)
        for nxt in dependents.get(cur, ()):
            if nxt not in blocked:
                stack.append(nxt)
    return blocked


def has_cycle(jobs):
    adj = {j.id: [d for d in j.deps if d in {x.id for x in jobs}] for j in jobs}
    color = {}

    def dfs(u):
        color[u] = 1
        for v in adj.get(u, ()):
            if color.get(v) == 1:
                return True
            if color.get(v, 0) == 0 and dfs(v):
                return True
        color[u] = 2
        return False

    return any(color.get(j.id, 0) == 0 and dfs(j.id) for j in jobs)
