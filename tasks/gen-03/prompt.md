实现当前目录 `period.py` 的 `minimal_period(s) -> int`:返回最小的正整数 p,使得 s 恰好是某个长度为 p 的串的整体重复(即 `s == s[:p] * (len(s) // p)`,且 p 整除 len(s))。

例如 `"aaaa"` → 1,`"abab"` → 2,`"abc"` → 3,`"aba"` → 3。空串抛 `ValueError`。

要求 O(n):隐藏测试含 20 万长度的串(逐个试除数的朴素法在部分构造串上会超时,可用 `(s+s).find(s,1)` 或 KMP 失配函数)。完成后与暴力对拍自测再结束。
