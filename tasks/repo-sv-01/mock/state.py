"""任务状态机。(mock 参考解)"""


class InvalidTransition(Exception):
    pass


ALLOWED = {
    ("PENDING", "RUNNING"),
    ("RUNNING", "SUCCEEDED"),
    ("RUNNING", "FAILED"),
    ("RUNNING", "CANCELLED"),
    ("RUNNING", "RETRYING"),
    ("FAILED", "RETRYING"),
    ("RETRYING", "PENDING"),
    ("PENDING", "CANCELLED"),
}


def transition(state, new):
    if (state, new) in ALLOWED:
        return new
    raise InvalidTransition(f"{state} -> {new}")
