当前目录的 `ledger.py` 是一个**只能在真实终端里运行**的记账程序:它会检查 stdin 是否为 tty,不是则直接拒绝运行。你的任务:让它在图形终端(xterm)里跑起来,并通过**向该窗口发送键盘输入**完成一串记账操作,使程序退出时在当前目录生成正确的 `ledger.txt`。

可用素材(环境已装好):`Xvfb`、`xterm`、`xdotool`。提示路径:启动一个虚拟 X 显示(注意 Xvfb 需要 `-ac` 免鉴权),在其中后台启动 `xterm -e python3 ledger.py`,等窗口出现后用 `xdotool` 按窗口名找到它并 `type` 输入、`key` 回车。

要求输入的命令序列(程序提示 `> `,逐行回车):

```
credit 1200
debit 350
credit 75
debit 90
balance arena
quit
```

规则与判定:

1. `credit/debit` 累计余额,`balance <name>` 把 `<name>:<余额>` 写入 `ledger.txt`(余额为 835 时写 `arena:835`),`quit` 退出;
2. 判定只看 `ledger.txt` 是否精确为 `arena:835\n`,且其 mtime 晚于你启动 Xvfb 前生成的 `.cu_start` 时间戳文件(`date +%s > .cu_start`);
3. 不得修改 `ledger.py`,不得直接创建/编辑 `ledger.txt`。

完成后自查再结束。
