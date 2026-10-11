当前目录 vendor 了真实流处理库 more-itertools 的旧版本(`more_itertools/`,源文件 5600+ 行)。用户报告 `ichunked(iterable, n)` 的边界行为有缺陷:

```python
from more_itertools import ichunked
list(map(list, ichunked([1, 2, 3], 0)))
# 当前抛 ValueError: Stop argument for islice() ... —— 把内部实现细节泄漏给了用户
```

期望行为(与上游后续版本一致):

1. `n < 0` → 抛 `ValueError('n must be at least 0')`;
2. `n == 0` → 不产出任何块,且**不得消费**输入迭代器中的任何元素(空迭代器与非空迭代器都如此);
3. 正常 `n >= 1` 的行为(含惰性/顺序语义)保持不变。

请在 5600 行的源文件中定位 `ichunked` 并修复;不得改动其他函数。完成后自测(含"source 未被消费")再结束。
