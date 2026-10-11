当前目录的构建脚本 `build.sh` 坏了:执行 `bash build.sh` 无法成功产出 `dist/output.txt`。仓库里有 `counter.py`(统计输入文件的**非空行**数并写出结果)和数据文件,脚本里引用的文件名与实际不符,输出目录也从未创建。

请修复,使 `bash build.sh` 在干净状态下(删掉 `dist/` 再跑)也能成功生成 `dist/output.txt`,内容为 `lines=<非空行数>`。可以改 `build.sh`,也可以用其他方式达成,但不得改动数据文件本身。完成后自查再结束。
