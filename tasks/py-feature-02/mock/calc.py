"""整数表达式求值器。(mock 参考解)"""


def _tokenize(s):
    toks = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
        elif c.isdigit():
            j = i
            while j < n and s[j].isdigit():
                j += 1
            toks.append(int(s[i:j]))
            i = j
        elif c in "+-*%()/":
            if c == "/" and i + 1 < n and s[i + 1] == "/":
                toks.append("//")
                i += 2
            else:
                toks.append(c)
                i += 1
        else:
            raise ValueError(f"非法字符: {c!r}")
    return toks


class _Parser:
    def __init__(self, toks):
        self.t = toks
        self.i = 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def take(self):
        tok = self.peek()
        self.i += 1
        return tok

    def parse(self):
        v = self.expr()
        if self.i != len(self.t):
            raise ValueError("多余 token")
        return v

    def expr(self):
        v = self.term()
        while self.peek() in ("+", "-"):
            op = self.take()
            w = self.term()
            v = v + w if op == "+" else v - w
        return v

    def term(self):
        v = self.factor()
        while self.peek() in ("*", "//", "%"):
            op = self.take()
            w = self.factor()
            if op == "*":
                v = v * w
            elif op == "//":
                v = v // w
            else:
                v = v % w
        return v

    def factor(self):
        tok = self.peek()
        if tok == "-":
            self.take()
            return -self.factor()
        if tok == "(":
            self.take()
            v = self.expr()
            if self.take() != ")":
                raise ValueError("括号不配对")
            return v
        if isinstance(tok, int):
            return self.take()
        raise ValueError("不完整的表达式")


def evaluate(expr):
    toks = _tokenize(expr)
    if not toks:
        raise ValueError("空表达式")
    return _Parser(toks).parse()
