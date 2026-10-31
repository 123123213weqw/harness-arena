import random

from mdrender import render


def oracle(text):
    """独立 oracle:正则分块 + 不同写法的行内处理。"""
    import re

    def repl(m):
        if m.group(1) is not None:
            return "<code>" + m.group(1) + "</code>"
        if m.group(2) is not None:
            return "<strong>" + m.group(2) + "</strong>"
        return "<em>" + m.group(3) + "</em>"

    def inline(s):
        # 位置优先:单遍 alternation,先出现者先替换(与参考解扫描语义一致)
        return re.sub(r"`([^`]*)`|\*\*(.*?)\*\*|\*([^*]*)\*", repl, s)

    lines = text.split("\n")
    out = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
        elif ln == "```":
            i += 1
            buf = []
            while i < len(lines) and lines[i] != "```":
                buf.append(lines[i])
                i += 1
            i += 1
            out.append("<pre><code>" + "\n".join(buf) + "\n</code></pre>")
        elif ln.startswith("### "):
            out.append(f"<h3>{inline(ln[4:])}</h3>"); i += 1
        elif ln.startswith("## "):
            out.append(f"<h2>{inline(ln[3:])}</h2>"); i += 1
        elif ln.startswith("# "):
            out.append(f"<h1>{inline(ln[2:])}</h1>"); i += 1
        elif ln.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(f"<li>{inline(lines[i][2:])}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
        else:
            buf = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(("# ", "## ", "### ", "```", "- ")):
                buf.append(lines[i])
                i += 1
            out.append("<p>" + inline(" ".join(buf)) + "</p>")
    return "\n".join(out)


def test_fixed():
    assert render("# T") == "<h1>T</h1>"
    assert render("a\nb") == "<p>a b</p>"
    assert render("- x\n- y") == "<ul><li>x</li><li>y</li></ul>"
    assert render("```\n*raw*\n```") == "<pre><code>*raw*\n</code></pre>"
    assert render("## *e* **b** `c`") == "<h2><em>e</em> <strong>b</strong> <code>c</code></h2>"
    assert render("# a\n\npara") == "<h1>a</h1>\n<p>para</p>"
    assert render("*") == "<p>*</p>"            # 不成对原样
    assert render("**") == "<p><em></em></p>"   # 空内容也成对
    assert render("``\n") == "<p><code></code></p>"


def test_random_against_oracle():
    rng = random.Random(77)
    words = ["a", "bb", "*i*", "**b**", "`c`", "**", "*", "x*y", "plain", "- not-list"]
    for _ in range(600):
        n = rng.randint(1, 10)
        body = []
        for _ in range(n):
            r = rng.random()
            if r < 0.15:
                body.append("")
            elif r < 0.3:
                body.append("# " + rng.choice(words))
            elif r < 0.45:
                body.append("- " + rng.choice(words))
            elif r < 0.55:
                body.append("```")
                body.append(rng.choice(words) + " *raw*")
                body.append("```")
            else:
                body.append(" ".join(rng.choice(words) for _ in range(rng.randint(1, 4))))
        t = "\n".join(body)
        assert render(t) == oracle(t), (t, render(t), oracle(t))
