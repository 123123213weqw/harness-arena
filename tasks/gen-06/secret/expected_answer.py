N = 1_234_567
EXPECTED = sum(
    1
    for x in range(1, N + 1)
    if x * x % 7 == 2 and x % 3 != 0
)
