当前目录 `rounding.py` 的 `my_round(x, ndigits=0)` 实现的是「加 0.5 取下整」舍入,有两个问题:

1. 舍入规则错误:要求是十进制「四舍六入五成双」(ROUND_HALF_EVEN),例如 `my_round(2.5) == 2`、`my_round(3.5) == 4`、`my_round(0.125, 2) == 0.12`、`my_round(2.675, 2) == 2.68`;
2. 二进制浮点误差:必须按十进制字符串语义处理数值(建议 `decimal` 模块、`Decimal(str(x))`),不能直接 `x * 10**ndigits`。

要求:保持函数签名与返回 float 类型不变;`ndigits` 可为负数(舍入到十/百位),如 `my_round(1234.5, -2) == 1200`;修完自测后结束。
