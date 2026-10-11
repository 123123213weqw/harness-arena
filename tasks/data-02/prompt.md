当前目录 `events.csv` 是脏的用户行为数据,请生成 `summary.csv`:

1. `user` 归一:转小写、去首尾空白;`minutes` 必须是十进制整数(允许首尾空白),且 >= 0,否则整行丢弃;空行丢弃;
2. `(user, event, minutes)` 三元组归一后完全相同的行视为重复,只保留一条;
3. 按 user 汇总所有保留行的 minutes 总和;
4. 输出表头 `user,total`;行按 total 降序,total 相同按 user 字典序升序;total 为十进制整数。

不得改动 `events.csv`。完成后自查再结束。
