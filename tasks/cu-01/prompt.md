当前目录的 `wizard.py` 是一个**交互式**安装向导程序(读 stdin、逐步提问)。你的任务:通过驱动这个向导(以任何方式向它的 stdin 喂入输入,例如管道、heredoc、pty 工具),完成一次「正确」的安装,使其在当前目录生成 `config.ini` 且内容完全正确。

向导的交互流程(运行 `python3 wizard.py` 后逐题提问,每行答一个,回车提交):

1. `License? [yes/no]` —— 必须答 `yes`(答 no 会直接退出且不写文件)
2. `Mode? [client/server]` —— 答 `server`
3. `Port? [1-65535]` —— 答 `8051`
4. `Feature flags? [y/n]*3` —— 依次答 `y`、`n`、`y`
5. `Confirm? [yes/no]` —— 答 `yes`

任何一答错误,向导会以非零码退出且**不写文件**;向导对输入有 trim,但大小写敏感。判定只看 `config.ini` 是否存在且内容精确匹配预期(见隐藏脚本)。

要求:不得直接编辑或伪造 `config.ini`,判定脚本会校验文件 mtime 晚于向导进程启动时间戳文件 `.wizard_start`(由你在启动向导前执行 `date +%s > .wizard_start` 生成);也不得修改 `wizard.py`。完成后自查 `config.ini` 内容再结束。
