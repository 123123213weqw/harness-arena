#!/usr/bin/env bash
set -euo pipefail
python3 - <<'EOF'
from html.parser import HTMLParser
from pathlib import Path

src = Path("profile.html").read_text(encoding="utf-8")

assert src.lstrip().lower().startswith("<!doctype html"), "缺 DOCTYPE"
assert "<script" not in src.lower(), "不得出现 script"
assert "style=" not in src.lower(), "不得内联样式"


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.events = []  # (kind, tag, attrs, text)
        self.imgs = []
        self.void = {"meta", "br", "hr", "img", "input", "link"}

    def handle_starttag(self, tag, attrs):
        self.stack.append(tag)
        self.events.append(("start", tag, dict(attrs), None))
        if tag == "img":
            self.imgs.append(dict(attrs))

    def handle_endtag(self, tag):
        self.events.append(("end", tag, {}, None))

    def handle_data(self, data):
        if data.strip():
            self.events.append(("text", None, {}, data.strip()))


p = P()
p.feed(src)
E = p.events


def text_after(tag, n=1):
    for i, (k, t, a, x) in enumerate(E):
        if k == "start" and t == tag:
            return next(x2 for k2, t2, a2, x2 in E[i + 1:] if k2 == "text")
    raise AssertionError(f"未找到 {tag}")


html_tag = next(a for k, t, a, x in E if k == "start" and t == "html")
assert html_tag.get("lang") == "zh-CN", "html lang 必须为 zh-CN"

metas = [a for k, t, a, x in E if k == "start" and t == "meta"]
assert any(a.get("charset", "").lower() == "utf-8" for a in metas), "缺 charset"
assert any(
    a.get("name") == "viewport" and "width=device-width" in a.get("content", "")
    for a in metas
), "viewport 不合规"

assert text_after("title") == "个人主页", "title 文本不符"

header_start = next(i for i, (k, t, a, x) in enumerate(E) if k == "start" and t == "header")
assert any(k == "start" and t == "h1" for k, t, a, x in E[header_start:]), "header 内无 h1"
assert text_after("h1") == "张三的个人主页", "h1 文本不符"

nav_start = next(i for i, (k, t, a, x) in enumerate(E) if k == "start" and t == "nav")
nav_end = next(i for i, (k, t, a, x) in enumerate(E) if k == "end" and t == "nav")
nav_inner = E[nav_start:nav_end]
lis = [a for k, t, a, x in nav_inner if k == "start" and t == "li"]
assert len(lis) == 3, f"nav>li 应为 3 个,得到 {len(lis)}"
for k, t, a, x in nav_inner:
    if k == "start" and t == "a":
        assert a.get("href"), "a 必须带 href"

secs = [a for k, t, a, x in E if k == "start" and t == "section"]
assert secs and any(a.get("id") for a in secs), "section 需带非空 id"
main_start = next(i for i, (k, t, a, x) in enumerate(E) if k == "start" and t == "main")
assert any(k == "start" and t == "h2" for k, t, a, x in E[main_start:]), "main 内无 h2"

forms = [a for k, t, a, x in E if k == "start" and t == "form"]
assert forms and forms[0].get("action"), "form 需带 action"
labels = [a for k, t, a, x in E if k == "start" and t == "label"]
assert any(a.get("for") == "email" for a in labels), "label for=email 缺失"
inputs = [a for k, t, a, x in E if k == "start" and t == "input"]
assert any(
    a.get("type") == "email" and a.get("id") == "email" and a.get("name") == "email"
    for a in inputs
), "email input 不合规"
buttons = [a for k, t, a, x in E if k == "start" and t == "button"]
assert any(a.get("type") == "submit" for a in buttons), "缺 submit button"

footer_start = next(i for i, (k, t, a, x) in enumerate(E) if k == "start" and t == "footer")
assert any(k == "text" and "2026" in x for k, t, a, x in E[footer_start:]), "footer 缺 2026"

for img in p.imgs:
    assert img.get("alt", "").strip(), "img 缺 alt"

print("eval-01 verified")
EOF
