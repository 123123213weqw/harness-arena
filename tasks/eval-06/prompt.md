实现当前目录 `cols.py` 的 Excel 列名与列号互转(**双射 26 进制**,无零位,A=1…Z=26,AA=27,AZ=52,BA=53,…,XFD=16384):

- `to_num(letters) -> int`:列名转列号;输入非空、只含 `A-Z` 大写字母,否则 `ValueError`;范围 1..2**31-1 之外(即超过 2**31-1)抛 `ValueError`;
- `to_letters(n) -> str`:列号转列名;`n` 必须为 `1 <= n <= 2**31-1` 的整数(bool 不算),否则 `ValueError`;
- 空串/小写/数字/空格均为非法。

完成后自测边界(A/Z/AA/AZ/BA/ZZ/AAA/XFD)与随机往返对拍再结束。
