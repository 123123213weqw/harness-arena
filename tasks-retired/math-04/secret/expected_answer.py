N = 1_000_000
sieve = bytearray([1]) * N
sieve[0] = sieve[1] = 0
for i in range(2, int(N**0.5) + 1):
    if sieve[i]:
        sieve[i * i :: i] = bytearray(len(sieve[i * i :: i]))
EXPECTED = sum(sieve)
