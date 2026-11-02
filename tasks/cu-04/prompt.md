当前目录的 `form.html` 是一个多步骤表单页面。你的任务:通过浏览器自动化(任何方式)填写并提交表单,使页面在 `#final` 中显示 SUCCESS。

表单规则:
1. **第 1 步**(默认):`#name` 输入框(必须恰好 6 个字母)、`#age` 输入框(必须 18-65 之间的整数),点击 `#next1` 进入第 2 步;
2. **第 2 步**:`#color` 下拉选择 `blue`、`#fruit` 下拉选择 `banana`,点击 `#next2` 进入第 3 步;
3. **第 3 步**:`#agree` 复选框必须勾选,点击 `#submit`;
4. 提交后 `#final` 显示 `SUCCESS` 或 `FAILED: <原因>`。

任何一步校验失败都会在 `#error` 中显示原因并**阻止前进**。你需要根据错误信息调整输入直到成功。

成功后,把页面上 `#final` 元素的完整文本(应为 `SUCCESS`)和 `#token` 元素的值(提交成功后出现的 8 位 token)写入 `answer.txt`,格式:`SUCCESS <token>`。

要求:不得修改 `form.html` 文件;不得直接解析 JS 源码来推算 token。

完成后自查 `answer.txt` 再结束。
