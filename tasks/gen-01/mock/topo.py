"""拓扑排序唯一性判定。(mock 参考解)"""
from collections import deque


def topo_order(n, edges):
    adj = [set() for _ in range(n)]
    indeg = [0] * n
    for a, b in set(edges):
        if b not in adj[a]:
            adj[a].add(b)
            indeg[b] += 1
    q = deque(i for i in range(n) if indeg[i] == 0)
    order = []
    while q:
        if len(q) > 1:
            return None  # 多解
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order if len(order) == n else None
