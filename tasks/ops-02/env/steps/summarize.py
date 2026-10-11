import argparse
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()

values = [
    int(line.rsplit(" ", 1)[1])
    for line in Path(args.input).read_text(encoding="utf-8").splitlines()
    if line.strip()
]

total = sum(values)
report = (
    f"total={total}\n"
    f"n={len(values)}\n"
)
Path(args.output).write_text(report, encoding="utf-8")
print("summarized")
