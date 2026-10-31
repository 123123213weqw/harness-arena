"""TTL + LRU 混合缓存。"""


class TTLCache:
    def __init__(self, capacity):
        raise NotImplementedError

    def get(self, key, now):
        raise NotImplementedError

    def put(self, key, value, now, ttl):
        raise NotImplementedError
