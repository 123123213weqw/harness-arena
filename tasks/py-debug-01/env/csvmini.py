"""单行 CSV 解析(带 bug)。"""


def split_line(line):
    """解析单行 CSV:引号包裹、字段内逗号、"" 转义;返回字段列表(未包裹的字面值)。"""
    fields = []
    cur = ""
    in_quotes = False
    i = 0
    while i < len(line):
        c = line[i]
        if c == '"':
            in_quotes = not in_quotes
        elif c == "," and not in_quotes:
            fields.append(cur)
            cur = ""
        else:
            cur += c
        i += 1
    fields.append(cur)
    return fields
