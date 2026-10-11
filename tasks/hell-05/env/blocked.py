"""取消链路与环检测。"""


def blocked_jobs(jobs, cancelled):
    """被取消任务及其(传递)依赖者全体,返回 id 集合。"""
    raise NotImplementedError


def has_cycle(jobs):
    """依赖图(只含 jobs 内部依赖边)是否有环。"""
    raise NotImplementedError
