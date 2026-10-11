"""本质不同子串计数。(mock 参考解,后缀自动机)"""


def count_distinct_substrings(s):
    length = [0]
    link = [-1]
    trans = [{}]
    last = 0

    for ch in s:
        cur = len(length)
        length.append(length[last] + 1)
        link.append(-1)
        trans.append({})

        p = last
        while p != -1 and ch not in trans[p]:
            trans[p][ch] = cur
            p = link[p]
        if p == -1:
            link[cur] = 0
        else:
            q = trans[p][ch]
            if length[p] + 1 == length[q]:
                link[cur] = q
            else:
                clone = len(length)
                length.append(length[p] + 1)
                link.append(link[q])
                trans.append(dict(trans[q]))
                while p != -1 and trans[p].get(ch) == q:
                    trans[p][ch] = clone
                    p = link[p]
                link[q] = clone
                link[cur] = clone
        last = cur

    return sum(length[v] - length[link[v]] for v in range(1, len(length)))
