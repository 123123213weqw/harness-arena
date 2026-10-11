"""调度规划。"""


def execution_order(jobs, cancelled=frozenset()):
    """按优先级(大者先,并列 id 小者先)返回可执行 id 序列;取消链路静默跳过;死锁抛 ValueError。"""
    raise NotImplementedError
