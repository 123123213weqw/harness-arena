"""markdown 子集 → HTML。(mock 参考解)"""
import re


def _inline(s):
    out = ""
    i = 0
    n = len(s)
    while i < n:
        if s[i] == "`":
            j = s.find("`", i + 1)
            if j != -1:
                out += "<code>" + s[i + 1 : j] + "</code>"
                i = j + 1
                continue
        if s.startswith("**", i):
            j = s.find("**", i + 2)
            if j != -1:
                out += "<strong>" + s[i + 2 : j] + "</strong>"
                i = j + 2
                continue
        if s[i] == "*":
            j = s.find("*", i + 1)
            if j != -1:
                out += "<em>" + s[i + 1 : j] + "</em>"
                i = j + 1
                continue
        out += s[i]
        i += 1
    return out


def render(text):
    blocks = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            buf = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # 跳过结束围栏
            blocks.append("<pre><code>" + "\n".join(buf) + "\n</code></pre>")
            continue
        if line.startswith("### "):
            blocks.append("<h3>" + _inline(line[4:]) + "</h3>")
            i += 1
        elif line.startswith("## "):
            blocks.append("<h2>" + _inline(line[3:]) + "</h2>")
            i += 1
        elif line.startswith("# "):
            blocks.append("<h1>" + _inline(line[2:]) + "</h1>")
            i += 1
        elif line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append("<li>" + _inline(lines[i][2:]) + "</li>")
                i += 1
            blocks.append("<ul>" + "".join(items) + "</ul>")
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "```", "- ")):
                para.append(lines[i])
                i += 1
            blocks.append("<p>" + _inline(" ".join(para)) + "</p>")
    return "\n".join(blocks)
