"""单行 CSV 解析。(mock 参考解)"""


def split_line(line):
    line = line.rstrip("\r\n")
    fields = []
    cur = ""
    i, n = 0, len(line)
    while i < n:
        c = line[i]
        if c == '"':
            i += 1
            while True:
                if i >= n:
                    raise ValueError("引号字段未闭合")
                if line[i] == '"':
                    if i + 1 < n and line[i + 1] == '"':
                        cur += '"'
                        i += 2
                        continue
                    i += 1
                    break
                cur += line[i]
                i += 1
        elif c == ",":
            fields.append(cur)
            cur = ""
            i += 1
        else:
            cur += c
            i += 1
    fields.append(cur)
    return fields
