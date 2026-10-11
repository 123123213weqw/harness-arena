"""任务状态机。"""


class InvalidTransition(Exception):
    pass


ALLOWED = {
    ("PENDING", "RUNNING"),
    ("RUNNING", "SUCCEEDED"),
    ("RUNNING", "FAILED"),
    ("RUNNING", "CANCELLED"),
    ("RUNNING", "RETRYING"),
    ("CANCELLED", "RUNNING"),   # 存疑:已取消的任务不应复活
    ("FAILED", "RETRYING"),
    ("FAILED", "PENDING"),      # 存疑:绕过了 RETRYING
    ("RETRYING", "PENDING"),
    ("PENDING", "CANCELLED"),
}


def transition(state, new):
    if (state, new) in ALLOWED:
        return new
    raise InvalidTransition(f"{state} -> {new}")
