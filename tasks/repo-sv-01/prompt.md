当前目录是一个小任务调度服务的三个模块(`scheduler.py` / `state.py` / `store.py`),集成测试暴露出三个生产事故级 bug,请全部修复:

1. **重试退避是线性的**:`scheduler.JobScheduler.run` 文档承诺失败重试按**指数退避**——第 k 次重试前等待 `base_delay * 2**(k-1)`(即 1s、2s、4s、8s...)。当前实现是 `base_delay * attempt`(1s、2s、3s...),高峰期造成重试风暴。修复后 `run` 返回的 `delays` 列表必须体现指数序列,成功路径与耗尽路径的行为不变;
2. **状态机越权转移**:`state.ALLOWED` 里混入了非法转移:`CANCELLED → RUNNING`(已取消的任务复活)与 `FAILED → PENDING`(绕过 RETRYING)。合法转移集(其余一律抛 `InvalidTransition`):`PENDING→RUNNING`、`RUNNING→{SUCCEEDED, FAILED, CANCELLED, RETRYING}`、`FAILED→RETRYING`、`RETRYING→PENDING`、`PENDING→CANCELLED`;
3. **快照别名泄漏**:`store.InMemoryStore.snapshot()` 返回内部字典的**活引用**,调用方改快照会污染存储。必须返回隔离副本。

要求:scheduler 的重试流程(失败→RETRYING→PENDING→RUNNING 循环)在修复后仍照常运转;不得改变模块/函数签名。修复后自测三条症状再结束。
