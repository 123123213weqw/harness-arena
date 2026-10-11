"""并查集。(mock 参考解)"""


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.n = n

    def _find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:  # 路径压缩
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self._find(a), self._find(b)
        if ra == rb:
            return
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        self.n -= 1

    def connected(self, a, b):
        return self._find(a) == self._find(b)

    def count(self):
        return self.n
