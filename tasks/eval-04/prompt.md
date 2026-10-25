实现当前目录 `meet.py` 的 `common_free(busy_by_person, window, min_len) -> list[tuple]`:

- `busy_by_person`:多人各自的忙碌区间列表(每人为 `[(start, end), ...]` 的列表,区间为半开 `[start, end)`,可能乱序、可能重叠、`start == end` 的空区间存在);
- `window`:公共时间窗 `(ws, we)`;
- 返回**窗口内所有人都空闲**的时间段,要求长度 `>= min_len`,且**极大合并**(相邻空闲段 [a,b) 与 [b,c) 应合并为 [a,c) 后再判长度),按起点升序;
- `ws >= we` 或 `min_len <= 0` 抛 `ValueError`;忙碌区间完全覆盖窗口时返回 `[]`;窗口外的忙碌部分忽略。

效率要求 O(B log B)(B 为全部忙碌区间数):隐藏测试含 20 万区间性能门,逐点扫描(O(ws-we))必超时。完成后与小规模暴力(逐单位时刻判所有人空闲)对拍自测再结束。
