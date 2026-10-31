#!/usr/bin/env python3
"""只能在真实 tty 里运行的记账程序;balance 写 ledger.txt,quit 退出。"""
import sys

if not sys.stdin.isatty():
    print("refused: stdin is not a terminal", flush=True)
    sys.exit(2)

bal = 0
print("ledger ready", flush=True)
while True:
    print("> ", end="", flush=True)
    line = sys.stdin.readline()
    if not line:
        break
    parts = line.strip().split()
    if not parts:
        continue
    cmd = parts[0]
    if cmd == "credit" and len(parts) == 2 and parts[1].lstrip("-").isdigit():
        bal += int(parts[1])
        print(f"ok bal={bal}", flush=True)
    elif cmd == "debit" and len(parts) == 2 and parts[1].lstrip("-").isdigit():
        bal -= int(parts[1])
        print(f"ok bal={bal}", flush=True)
    elif cmd == "balance" and len(parts) == 2:
        with open("ledger.txt", "w", encoding="utf-8") as f:
            f.write(f"{parts[1]}:{bal}\n")
        print("written", flush=True)
    elif cmd == "quit":
        print("bye", flush=True)
        break
    else:
        print("err: unknown command", flush=True)
