实现当前目录 `ttlcache.py` 的 `TTLCache`(当前为占位抛错):带 TTL 过期的 LRU 缓存。所有操作显式传入当前时刻 `now`(单调递增整数,不依赖系统时钟)。

- `TTLCache(capacity)`:capacity 为正整数,否则 `ValueError`;
- `put(key, value, now, ttl)`:写入;过期时刻为 `now + ttl`(ttl 为正整数,否则 ValueError)。键已存在(且未过期)则**更新值与过期时刻,并刷新 LRU 序**;容量满时先**逐出最久未使用且仍有效**的键再写入(过期键在任意操作中应被惰性清除,被逐出的具体键遵循 LRU 序);
- `get(key, now) -> value | None`:命中且未过期返回值并**刷新 LRU 序**(过期时刻不变);过期或不存在返回 None(过期的同时把它移除);
- `__len__`:当前有效条目数(不触发全量清扫,按结构内计数即可,需与惰性删除一致)。

隐藏测试:随机操作序列对拍独立 oracle(用 `dict` 保序模拟)与边界用例。完成后自测再结束。
