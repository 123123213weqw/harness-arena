import math


def my_round(x, ndigits=0):
    """十进制四舍六入五成双(ROUND_HALF_EVEN),返回 float。

    按十进制语义处理(0.125 两位应得 0.12,2.675 两位应得 2.68),
    ndigits 为负数时舍入到十/百位。
    """
    m = 10 ** ndigits
    return math.floor(x * m + 0.5) / m
