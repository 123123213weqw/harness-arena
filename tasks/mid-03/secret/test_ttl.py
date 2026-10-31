import random

import pytest

from ttlcache import TTLCache


def test_basics():
    c = TTLCache(2)
    c.put("a", 1, now=0, ttl=10)
    c.put("b", 2, now=1, ttl=10)
    assert c.get("a", now=2) == 1        # 刷新 a
    c.put("c", 3, now=3, ttl=10)         # 逐出 b
    assert c.get("b", now=4) is None
    assert c.get("a", now=5) == 1


def test_expiry_semantics():
    c = TTLCache(2)
    c.put("x", 9, now=0, ttl=5)          # 过期时刻 5
    assert c.get("x", now=4) == 9        # 5 前有效
    assert c.get("x", now=5) is None     # now>=expire 判过期
    assert len(c) == 0


def test_get_does_not_extend_ttl():
    c = TTLCache(1)
    c.put("x", 1, now=0, ttl=3)
    assert c.get("x", now=2) == 1        # 命中刷新 LRU 但不改过期
    assert c.get("x", now=3) is None


def test_overwrite_refreshes():
    c = TTLCache(1)
    c.put("x", 1, now=0, ttl=2)
    c.put("x", 2, now=1, ttl=10)         # 更新值+新过期时刻
    assert c.get("x", now=5) == 2


def test_expired_freed_capacity():
    c = TTLCache(1)
    c.put("a", 1, now=0, ttl=1)
    c.put("b", 2, now=5, ttl=10)         # a 已过期,应直接写入而非逐出 b 再挤
    assert c.get("b", now=6) == 2
    assert len(c) == 1


@pytest.mark.parametrize("bad", [0, -1, 1.5, True])
def test_bad_capacity(bad):
    with pytest.raises(ValueError):
        TTLCache(bad)


def test_bad_ttl():
    c = TTLCache(2)
    for bad in (0, -3, 2.5, True):
        with pytest.raises(ValueError):
            c.put("k", 1, now=0, ttl=bad)


def test_random_against_oracle():
    class Oracle:
        def __init__(self, cap):
            self.cap = cap
            self.items = {}  # key -> [value, expire, last_use]

        def get(self, k, now):
            it = self.items.get(k)
            if it and it[1] > now:
                it[2] = now
                return it[0]
            if it:
                del self.items[k]
            return None

        def put(self, k, v, now, ttl):
            if k in self.items:
                self.items[k] = [v, now + ttl, now]
                return
            if len(self.items) >= self.cap:
                victim = min(self.items, key=lambda x: self.items[x][2])
                del self.items[victim]
            self.items[k] = [v, now + ttl, now]

    rng = random.Random(99)
    for _ in range(60):
        cap = rng.randint(1, 5)
        c, o = TTLCache(cap), Oracle(cap)
        for step in range(400):
            now = step
            k = rng.randint(0, 8)
            if rng.random() < 0.55:
                v = rng.randint(0, 99)
                ttl = rng.randint(1, 12)
                c.put(k, v, now, ttl)
                o.put(k, v, now, ttl)
            else:
                assert c.get(k, now) == o.get(k, now), (step, k)
