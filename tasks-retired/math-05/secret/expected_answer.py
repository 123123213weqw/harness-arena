N = 10**12
sq = int(N**0.5)
while (sq + 1) ** 2 <= N:
    sq += 1
while sq**2 > N:
    sq -= 1
cb = round(N ** (1 / 3))
while (cb + 1) ** 3 <= N:
    cb += 1
while cb**3 > N:
    cb -= 1
sx = round(N ** (1 / 6))
while (sx + 1) ** 6 <= N:
    sx += 1
while sx**6 > N:
    sx -= 1
EXPECTED = sq + cb - sx
