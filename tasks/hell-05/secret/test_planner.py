import random

import pytest

from blocked import blocked_jobs, has_cycle
from jobs import Job
from planner import execution_order


def test_priority_order():
    jobs = [Job("a", 1), Job("b", 5), Job("c", 3)]
    assert execution_order(jobs) == ["b", "c", "a"]


def test_tie_break_by_id():
    jobs = [Job("z", 2), Job("a", 2), Job("m", 2)]
    assert execution_order(jobs) == ["a", "m", "z"]


def test_dependency_chain():
    jobs = [Job("c", 9, ["b"]), Job("b", 9, ["a"]), Job("a", 0)]
    assert execution_order(jobs) == ["a", "b", "c"]


def test_mixed():
    jobs = [Job("a", 1), Job("b", 2), Job("c", 10, ["a", "b"])]
    assert execution_order(jobs) == ["b", "a", "c"]


def test_external_deps_count_as_done():
    jobs = [Job("x", 1, ["ghost", "phantom"])]
    assert execution_order(jobs) == ["x"]


def test_duplicate_ids_rejected():
    with pytest.raises(ValueError):
        execution_order([Job("a", 1), Job("a", 2)])


def test_cycle_raises():
    jobs = [Job("a", 1, ["b"]), Job("b", 1, ["a"])]
    with pytest.raises(ValueError, match="cycle"):
        execution_order(jobs)
    assert has_cycle(jobs) is True


def test_cancel_silences_cycle():
    jobs = [Job("a", 1, ["b"]), Job("b", 1, ["a"])]
    assert execution_order(jobs, cancelled={"a"}) == []
    assert has_cycle([jobs[1]]) is False


def test_blocked_propagation():
    jobs = [
        Job("root", 5),
        Job("mid", 4, ["root"]),
        Job("leaf", 3, ["mid"]),
        Job("independent", 1),
    ]
    assert blocked_jobs(jobs, {"mid"}) == {"mid", "leaf"}
    assert execution_order(jobs, cancelled={"mid"}) == ["root", "independent"]


def test_cancelled_job_never_runs():
    jobs = [Job("a", 9), Job("b", 1)]
    assert execution_order(jobs, cancelled={"a"}) == ["b"]


def test_empty():
    assert execution_order([]) == []
    assert execution_order([Job("a", 1)], cancelled={"a"}) == []


def brute_order(jobs, cancelled):
    jobs = list(jobs)
    ids = [j.id for j in jobs]
    assert len(ids) == len(set(ids))
    known = {j.id for j in jobs}
    done = set(cancelled)
    # 传递取消
    changed = True
    while changed:
        changed = False
        for j in jobs:
            if j.id not in done and any(d in known and d in done for d in j.deps):
                done.add(j.id)
                changed = True
    order = []
    finished = set()
    while True:
        ready = [
            j for j in jobs
            if j.id not in done and j.id not in finished
            and all(d not in known or d in finished for d in j.deps)
        ]
        if not ready:
            break
        pick = sorted(ready, key=lambda j: (-j.priority, j.id))[0]
        order.append(pick.id)
        finished.add(pick.id)
    leftover = [j.id for j in jobs if j.id not in done and j.id not in finished]
    assert not leftover, "brute 假设无环"
    return order


def test_random_against_brute():
    random.seed(91)
    for _ in range(60):
        n = random.randint(1, 12)
        ids = [f"t{i}" for i in range(n)]
        jobs = [
            Job(i, random.randint(-3, 3), random.sample(ids[:k], random.randint(0, min(k, 3))))
            for k, i in enumerate(ids)
        ]  # deps 只指向更早的 id → 天然无环
        cancelled = random.sample(ids, random.randint(0, min(2, n)))
        assert execution_order(jobs, cancelled=set(cancelled)) == brute_order(jobs, set(cancelled))
