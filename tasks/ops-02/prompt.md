当前目录是一条三步数据管线,`bash pipeline.sh` 目前跑不通:

- `steps/prepare.py`:读 `raw.log`(每行 `名字,数值`),规范化(名字去空白转小写、数值转 int,跳过空行),写 `tmp/items.txt`(每行 `名字 数值`);
- `steps/filter.py`:读 items 文件,只保留**数值 >= 过滤阈值**的行。阈值从环境变量 `THRESHOLD` 读取(整数)——正确取值应为 **15**;
- `steps/summarize.py`:读过滤结果,写 `dist/summary.txt`,精确格式为四行:
  `sum=<保留行数值总和>`
  `kept=<保留行数>`
  `dropped=<被丢弃行数>`
  `avg=<保留行均值,两位小数;无保留行则 0.00>`

故障点不止一个:输出目录从未创建;`pipeline.sh` 没给 `THRESHOLD`;`summarize.py` 输出的字段名和格式不对。请修复,使干净状态(删掉 `tmp/` 与 `dist/` 后)执行 `bash pipeline.sh` 能产出正确摘要;不得改动 `raw.log` 与 `steps/prepare.py` 的规范化语义。完成后自查再结束。
