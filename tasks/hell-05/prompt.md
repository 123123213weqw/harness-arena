当前目录是一个任务编排模块组:`jobs.py`(Job 定义,已给出)、`planner.py`(需实现)、`blocked.py`(需实现)。请实现跨这两个模块的调度规划:

## 语义

- `planner.execution_order(jobs, cancelled=frozenset()) -> list[str]`:返回可执行任务的 id 序列。规则:反复在「所有依赖均已完成且尚未被调度」的任务中,选 **priority 最大者;并列时 id 字典序最小者**;被选中即视为完成,释放其依赖者;
- 依赖:`Job(id, priority, deps)`,deps 为 id 列表;不在 jobs 里的依赖 id 视为外部已完成任务;
- 取消语义(实现于 `blocked.py` 的 `blocked_jobs(jobs, cancelled) -> set[str]`):被取消的任务**永远无法完成**,依赖它(直接或传递)的任务同样永远无法运行——这些任务全部**静默跳过**(不进序列、不报错);`execution_order` 必须用 `blocked_jobs` 排除它们后再规划;
- 死锁:`blocked.py` 还需提供 `has_cycle(jobs) -> bool`:在**排除取消链路后**的剩余依赖图上检测环;`execution_order` 在剩余图死锁时抛 `ValueError("cycle")`;
- 空输入返回空列表;`jobs` 中 id 不得重复(重复抛 `ValueError`)。

不得修改 `jobs.py`。完成后自测(优先级/并列/取消传播/环)再结束。
