"""O(1) LRU 缓存。(mock 参考解)"""


class LRUCache:
    def __init__(self, capacity):
        if not isinstance(capacity, int) or capacity <= 0:
            raise ValueError("capacity 必须为正整数")
        self.cap = capacity
        self.d = {}  # dict 保序:尾部最新

    def get(self, key):
        if key not in self.d:
            return -1
        v = self.d.pop(key)
        self.d[key] = v
        return v

    def put(self, key, value):
        if key in self.d:
            self.d.pop(key)
        self.d[key] = value
        if len(self.d) > self.cap:
            del self.d[next(iter(self.d))]
