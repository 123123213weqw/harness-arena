import argparse
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()

out_lines = []
for line in Path(args.input).read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line:
        continue
    name, _, value = line.partition(",")
    out_lines.append(f"{name.strip().lower()} {int(value.strip())}")

Path(args.output).write_text("\n".join(out_lines) + "\n", encoding="utf-8")
print(f"prepared {len(out_lines)} items")
