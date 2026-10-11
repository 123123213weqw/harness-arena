"""矩阵快速幂。(mock 参考解)"""


def _mul(A, B, mod, n):
    C = [[0] * n for _ in range(n)]
    for i in range(n):
        Ai, Ci = A[i], C[i]
        for k in range(n):
            a = Ai[k]
            if a:
                Bk = B[k]
                for j in range(n):
                    Ci[j] = (Ci[j] + a * Bk[j]) % mod
    return C


def count_walks(n, edges, L, s, t, mod):
    M = [[0] * n for _ in range(n)]
    for u, v in edges:
        M[u][v] = (M[u][v] + 1) % mod
    R = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    base = M
    e = L
    while e:
        if e & 1:
            R = _mul(R, base, mod, n)
        base = _mul(base, base, mod, n)
        e >>= 1
    return R[s][t] % mod
