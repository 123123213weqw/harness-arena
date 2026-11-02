当前目录的 `app.html` 是一个本地交互式网页(纯前端,无需服务器)。你的任务:通过**浏览器自动化**(任何你可用的方式:agent-browser CLI、Playwright Python、Chrome headless 命令行、curl+解析等)与页面交互,提取隐藏数据并写入 `result.txt`。

页面结构:
1. 打开时有 3 个选项卡按钮(`#tab-a`、`#tab-b`、`#tab-c`),每个选项卡显示不同的内容;
2. 默认显示选项卡 A(一组整数);
3. 点击 `#tab-b` 显示一组键值对;
4. 点击 `#tab-c` 显示一个输入框和按钮 `#calc`;
5. 在 `#input` 中输入选项卡 A 中所有整数的**和**,然后点击 `#calc`,页面会在 `#output` 中显示一个解锁码。

你的任务:提取该解锁码(一个 6 位十六进制字符串),写入 `result.txt`(仅一行,格式 `CODE=<hex>`,如 `CODE=a1b2c3`)。

要求:不得直接读或解析 `app.html` 的 JavaScript 源码来计算解锁码(判定会检查源文件 mtime);必须通过浏览器/HTTP 交互获取页面内容。

完成后自查 `result.txt` 内容再结束。
