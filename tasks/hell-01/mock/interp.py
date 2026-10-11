"""MINI 语言解释器。(mock 参考解)"""
import operator

MAX_STEPS = 10**6

_CMP = {
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}


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
        elif c.islower():
            j = i
            while j < n and s[j].islower():
                j += 1
            toks.append(s[i:j])
            i = j
        elif s.startswith(("==", "!=", "<=", ">="), i):
            toks.append(s[i : i + 2])
            i += 2
        elif c in "+-*/%()<>=!":
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

    def expr(self):
        node = self.add()
        while self.peek() in ("==", "!=", "<", "<=", ">", ">="):
            op = self.take()
            node = (op, node, self.add())
        return node

    def add(self):
        node = self.mul()
        while self.peek() in ("+", "-"):
            op = self.take()
            node = (op, node, self.mul())
        return node

    def mul(self):
        node = self.unary()
        while self.peek() in ("*", "/", "%"):
            op = self.take()
            node = (op, node, self.unary())
        return node

    def unary(self):
        if self.peek() == "-":
            self.take()
            return ("neg", self.unary())
        if self.peek() == "+":
            self.take()
            return self.unary()
        return self.primary()

    def primary(self):
        tok = self.peek()
        if tok == "(":
            self.take()
            node = self.expr()
            if self.take() != ")":
                raise ValueError("括号不配对")
            return node
        if isinstance(tok, int):
            self.take()
            return ("num", tok)
        if isinstance(tok, str) and tok.islower() and tok.isalpha():
            self.take()
            return ("var", tok)
        raise ValueError("不完整的表达式")

    def finish(self):
        node = self.expr()
        if self.i != len(self.t):
            raise ValueError("多余 token")
        return node


def _parse_expr_tokens(toks):
    return _Parser(toks).finish()


def _parse_stmt(line):
    """单条简单语句(print/赋值)→ AST;控制语句由上层处理。"""
    toks = _tokenize(line)
    if not toks:
        raise ValueError("空语句")
    if toks[0] == "print":
        return ("print", _parse_expr_tokens(toks[1:]))
    if (
        len(toks) >= 3
        and isinstance(toks[0], str)
        and toks[0].isalpha()
        and toks[1] == "="
    ):
        return ("assign", toks[0], _parse_expr_tokens(toks[2:]))
    raise ValueError("非法语句")


def _parse_line(line):
    head, sep, body = line.partition(":")
    h = head.strip()
    if h.startswith("if ") or h.startswith("while "):
        if not sep:
            raise ValueError("控制语句缺冒号")
        kind = "if" if h.startswith("if ") else "while"
        cond_src = h[2:].strip() if kind == "if" else h[5:].strip()
        cond = _parse_expr_tokens(_tokenize(cond_src))
        body_stmts = []
        for part in body.split(";"):
            if not part.strip():
                raise ValueError("空语句")
            body_stmts.append(_parse_stmt(part))
        return (kind, cond, body_stmts)
    if sep:
        raise ValueError("简单语句不含冒号")
    return _parse_stmt(line.strip())


def _eval(node, env):
    kind = node[0]
    if kind == "num":
        return node[1]
    if kind == "var":
        if node[1] not in env:
            raise ValueError(f"未定义变量: {node[1]}")
        return env[node[1]]
    if kind == "neg":
        return -_eval(node[1], env)
    a = _eval(node[1], env)
    b = _eval(node[2], env)
    if kind == "+":
        return a + b
    if kind == "-":
        return a - b
    if kind == "*":
        return a * b
    if b == 0:
        raise ValueError("division by zero")
    if kind == "/":
        return a // b
    if kind == "%":
        return a % b
    return 1 if _CMP[kind](a, b) else 0


def run(program):
    asts = [_parse_line(line) for line in program]  # 语法检查先行
    env = {}
    out = []
    steps = [0]

    def exec_stmt(stmt):
        steps[0] += 1
        if steps[0] > MAX_STEPS:
            raise RuntimeError("超出语句执行上限")
        k = stmt[0]
        if k == "print":
            out.append(str(_eval(stmt[1], env)))
        elif k == "assign":
            env[stmt[1]] = _eval(stmt[2], env)
        elif k == "if":
            if _eval(stmt[1], env) != 0:
                for s in stmt[2]:
                    exec_stmt(s)
        else:  # while
            while _eval(stmt[1], env) != 0:
                for s in stmt[2]:
                    exec_stmt(s)

    for stmt in asts:
        exec_stmt(stmt)
    return out
