from decimal import ROUND_HALF_EVEN, Decimal


def my_round(x, ndigits=0):
    """十进制四舍六入五成双(ROUND_HALF_EVEN),返回 float。(mock 参考解)"""
    q = Decimal(str(x)).quantize(
        Decimal(1).scaleb(-ndigits), rounding=ROUND_HALF_EVEN
    )
    return float(q)
