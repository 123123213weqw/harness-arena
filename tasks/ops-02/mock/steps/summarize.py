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

s = sum(values)
avg = f"{s / len(values):.2f}" if values else "0.00"
report = (
    f"sum={s}\n"
    f"kept={len(values)}\n"
    f"dropped={Path('tmp/items.txt').read_text(encoding='utf-8').count(chr(10)) - len(values)}\n"
    f"avg={avg}\n"
)
Path(args.output).write_text(report, encoding="utf-8")
print("summarized")
