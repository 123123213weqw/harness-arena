import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description="统计输入文件的非空行数并写出结果")
parser.add_argument("--input", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()

n = len([l for l in Path(args.input).read_text(encoding="utf-8").splitlines() if l.strip()])
Path(args.output).write_text(f"lines={n}\n", encoding="utf-8")
print(f"wrote {args.output}")
