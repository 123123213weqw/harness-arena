import random
import time

import pytest

from lrucache import LRUCache


def test_basic():
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    assert c.get(1) == 1
    c.put(3, 3)  # 逐出 2(1 被 get 刚用过)
    assert c.get(2) == -1
    assert c.get(3) == 3


def test_evict_order_and_get_refresh():
    c = LRUCache(3)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    assert c.get("a") == 1          # a 变最近使用
    c.put("d", 4)                   # 逐出 b
    assert c.get("b") == -1
    assert c.get("a") == 1
    assert c.get("c") == 3
    assert c.get("d") == 4


def test_overwrite_keeps_recency():
    c = LRUCache(2)
    c.put(1, 10)
    c.put(2, 20)
    c.put(1, 11)                    # 更新 1 → 最近使用
    c.put(3, 30)                    # 逐出 2
    assert c.get(2) == -1
    assert c.get(1) == 11


def test_capacity_one_and_zero_values():
    c = LRUCache(1)
    c.put("k", 0)
    assert c.get("k") == 0          # 0 是合法值,不是 miss
    c.put("m", 5)
    assert c.get("k") == -1
    assert c.get("m") == 5


def test_bad_capacity():
    with pytest.raises(ValueError):
        LRUCache(0)
    with pytest.raises(ValueError):
        LRUCache(-3)


def test_reference_oracle_random():
    class Oracle:
        def __init__(self, cap):
            self.cap = cap
            self.d = {}

        def get(self, k):
            if k not in self.d:
                return -1
            self.d[k] = self.d.pop(k)
            return self.d[k]

        def put(self, k, v):
            if k in self.d:
                self.d.pop(k)
            self.d[k] = v
            if len(self.d) > self.cap:
                del self.d[next(iter(self.d))]

    random.seed(8)
    for _ in range(50):
        cap = random.randint(1, 8)
        c, o = LRUCache(cap), Oracle(cap)
        for _ in range(400):
            k = random.randint(0, 12)
            if random.random() < 0.5:
                assert c.get(k) == o.get(k)
            else:
                v = random.randint(0, 99)
                c.put(k, v)
                o.put(k, v)
                assert c.get(k) == v


def test_performance():
    random.seed(6)
    c = LRUCache(256)
    t0 = time.time()
    for i in range(300_000):
        k = random.randint(0, 511)
        if random.random() < 0.6:
            c.get(k)
        else:
            c.put(k, i)
    assert time.time() - t0 < 3, "太慢:get/put 应为 O(1)"
