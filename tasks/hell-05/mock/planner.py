"""调度规划。(mock 参考解)"""
import heapq

from blocked import blocked_jobs, has_cycle
from jobs import Job  # noqa: F401


def execution_order(jobs, cancelled=frozenset()):
    ids = [j.id for j in jobs]
    if len(ids) != len(set(ids)):
        raise ValueError("重复的任务 id")

    blocked = blocked_jobs(jobs, cancelled)
    alive = [j for j in jobs if j.id not in blocked]
    if has_cycle(alive):
        raise ValueError("cycle")

    known = {j.id for j in alive}
    remaining_deps = {j.id: sum(1 for d in j.deps if d in known) for j in alive}
    dependents = {}
    for j in alive:
        for d in j.deps:
            if d in known:
                dependents.setdefault(d, set()).add(j.id)

    heap = [(-j.priority, j.id) for j in alive if remaining_deps[j.id] == 0]
    heapq.heapify(heap)
    order = []
    done = set()
    while heap:
        _p, jid = heapq.heappop(heap)
        order.append(jid)
        done.add(jid)
        for nxt in dependents.get(jid, ()):
            remaining_deps[nxt] -= 1
            if remaining_deps[nxt] == 0:
                nxt_job = next(j for j in alive if j.id == nxt)
                heapq.heappush(heap, (-nxt_job.priority, nxt))
    return order
