import random
import time
from functools import lru_cache

from game import winner


def oracle(piles):
    @lru_cache(maxsize=None)
    def win(state):
        state = tuple(state)
        for idx, p in enumerate(state):
            for a in range(1, p):
                b = p - a
                if a == b:
                    continue
                rest = tuple(
                    sorted(state[:idx] + state[idx + 1 :] + (a, b))
                )
                if not win(rest):
                    return True
        return False

    return "First" if win(tuple(sorted(piles))) else "Second"


def _partitions(total, max_part):
    if total == 0:
        yield ()
        return
    for first in range(min(total, max_part), 0, -1):
        for rest in _partitions(total - first, first):
            yield (first,) + rest


def test_exhaustive_small():
    for total in range(1, 11):
        for state in _partitions(total, total):
            assert winner(list(state)) == oracle(state), state


def test_fixed():
    assert winner([]) == "Second"
    assert winner([1]) == "Second"
    assert winner([3]) == "First"          # 3 → 1+2,对手无路可走
    assert winner([1, 1]) == "Second"
    assert winner([1, 2, 3]) == "First"


def test_random_small_against_oracle():
    random.seed(37)
    for _ in range(60):
        piles = [
            random.randint(1, 7) for _ in range(random.randint(1, 4))
        ]
        assert winner(piles) == oracle(tuple(piles)), piles


def test_big_fast():
    random.seed(38)
    piles = [random.randint(1, 2000) for _ in range(100_000)]
    t0 = time.time()
    got = winner(piles)
    dt = time.time() - t0
    assert dt < 3, f"太慢: {dt:.1f}s,应预计算 Grundy 数后异或"
    assert got in ("First", "Second")
