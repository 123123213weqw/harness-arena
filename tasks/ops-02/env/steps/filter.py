import argparse
import os
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--input", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()

threshold = int(os.environ["THRESHOLD"])  # 必须由调用方提供

kept = []
for line in Path(args.input).read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    name, value = line.rsplit(" ", 1)
    if int(value) >= threshold:
        kept.append(line)

Path(args.output).write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
print(f"kept {len(kept)} lines")
