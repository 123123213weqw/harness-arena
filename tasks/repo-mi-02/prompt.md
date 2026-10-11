当前目录 vendor 了真实流处理库 more-itertools 的旧版本(`more_itertools/`)。`constrained_batches(iterable, max_size, max_count=None)` 支持 `max_count` 限制每块条数,但**没有校验 `max_count` 的合法性**:`max_count=0` 或负数时会进入未定义行为而不是干净报错。

期望行为(与上游后续版本一致):

1. `max_count is not None and max_count <= 0` → 抛 `ValueError('maximum count must be greater than zero')`,且**不得消费**输入迭代器的任何元素(抛错前后 source 应保持原样可继续取值);
2. `max_size <= 0` 的既有校验保持不变;
3. 正常分块行为(含 `max_count=1`、`max_count=2` 与无 `max_count`)不变。

请在源文件中定位 `constrained_batches` 并补上校验;不得改动其他函数。完成后自测再结束。
