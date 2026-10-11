import random
import time

from substrings import count_distinct_substrings


def brute(s):
    return len({s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1)})


def test_fixed():
    assert count_distinct_substrings("a") == 1
    assert count_distinct_substrings("aa") == 2
    assert count_distinct_substrings("ab") == 3
    assert count_distinct_substrings("aaa") == 3
    assert count_distinct_substrings("abab") == 7  # a b ab ba aba bab abab
    assert count_distinct_substrings("abc") == 6
    assert count_distinct_substrings("aab") == 5   # a aa aab ab b


def test_all_same_char_long():
    s = "a" * 100000
    assert count_distinct_substrings(s) == 100000


def test_random_against_brute():
    random.seed(84)
    for _ in range(120):
        n = random.randint(1, 60)
        alpha = random.choice(["ab", "abc", "abcde"])
        s = "".join(random.choice(alpha) for _ in range(n))
        assert count_distinct_substrings(s) == brute(s), s


def test_periodic():
    s = "ababab" * 5
    assert count_distinct_substrings(s) == brute(s)


def test_big_high_entropy_fast():
    rng = random.Random(85)
    s = "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(200_000))
    t0 = time.time()
    got = count_distinct_substrings(s)
    dt = time.time() - t0
    assert dt < 4, f"太慢: {dt:.1f}s,应后缀自动机/数组"
    # 高熵串答案 ≈ n(n+1)/2(极少数重复),做量级校验
    assert got > 200_000 * 199_000 // 2
