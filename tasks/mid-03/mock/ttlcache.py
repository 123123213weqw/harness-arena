"""TTL + LRU 混合缓存。(mock 参考解)"""
from collections import OrderedDict


class TTLCache:
    def __init__(self, capacity):
        if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity <= 0:
            raise ValueError("capacity 必须为正整数")
        self.cap = capacity
        self.d = OrderedDict()  # key -> (value, expire)

    def _purge(self, key, now):
        item = self.d.get(key)
        if item is not None and item[1] <= now:
            del self.d[key]

    def get(self, key, now):
        self._purge(key, now)
        if key not in self.d:
            return None
        self.d.move_to_end(key)
        return self.d[key][0]

    def put(self, key, value, now, ttl):
        if not isinstance(ttl, int) or isinstance(ttl, bool) or ttl <= 0:
            raise ValueError("ttl 必须为正整数")
        self._purge(key, now)
        if key in self.d:
            self.d[key] = (value, now + ttl)
            self.d.move_to_end(key)
            return
        while len(self.d) >= self.cap:
            self.d.popitem(last=False)
        self.d[key] = (value, now + ttl)

    def __len__(self):
        return len(self.d)
