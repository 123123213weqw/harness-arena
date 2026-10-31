#!/usr/bin/env python3
"""交互式安装向导:逐步提问,全部答对才写出 config.ini。"""
import sys


def ask(prompt):
    print(prompt, flush=True)
    line = sys.stdin.readline()
    if not line:
        print("EOF: aborted", flush=True)
        sys.exit(3)
    return line.strip()


answers = []
q1 = ask("License? [yes/no]")
if q1 != "yes":
    print("license declined", flush=True)
    sys.exit(1)
q2 = ask("Mode? [client/server]")
if q2 != "server":
    print("bad mode", flush=True)
    sys.exit(1)
q3 = ask("Port? [1-65535]")
if not (q3.isdigit() and 1 <= int(q3) <= 65535 and q3 == "8051"):
    print("bad port", flush=True)
    sys.exit(1)
flags = []
for name in ("alpha", "beta", "gamma"):
    f = ask(f"Enable {name}? [y/n]")
    if f not in ("y", "n"):
        print("bad flag", flush=True)
        sys.exit(1)
    flags.append(f)
q5 = ask("Confirm? [yes/no]")
if q5 != "yes":
    print("not confirmed", flush=True)
    sys.exit(1)

with open("config.ini", "w", encoding="utf-8") as f:
    f.write("[install]\n")
    f.write("mode=server\n")
    f.write("port=8051\n")
    f.write("alpha=1\n" if flags[0] == "y" else "alpha=0\n")
    f.write("beta=1\n" if flags[1] == "y" else "beta=0\n")
    f.write("gamma=1\n" if flags[2] == "y" else "gamma=0\n")
print("installed", flush=True)
