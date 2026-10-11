"""最小循环节。(mock 参考解)"""


def minimal_period(s):
    if not s:
        raise ValueError("空串无周期")
    return (s + s).find(s, 1)
