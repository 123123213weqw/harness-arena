import pytest

from scheduler import JobScheduler
from state import InvalidTransition, transition
from store import InMemoryStore


def test_success_path():
    st = InMemoryStore()
    ok, delays = JobScheduler(st).run("j1", lambda: None)
    assert ok is True and delays == []
    assert st.get("j1") == "SUCCEEDED"


def test_exponential_backoff():
    st = InMemoryStore()

    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] <= 2:
            raise RuntimeError("boom")

    ok, delays = JobScheduler(st, base_delay=1.0).run("j2", flaky)
    assert ok is True
    assert delays == [1.0, 2.0]
    assert st.get("j2") == "SUCCEEDED"

    calls2 = {"n": 0}

    def flaky3():
        calls2["n"] += 1
        if calls2["n"] <= 3:
            raise RuntimeError("boom")

    ok2, delays2 = JobScheduler(st, base_delay=2.0).run("j3", flaky3)
    assert ok2 is True
    assert delays2 == [2.0, 4.0, 8.0]


def test_exhaustion():
    st = InMemoryStore()
    boom = lambda: (_ for _ in ()).throw(RuntimeError)  # noqa: E731
    ok, delays = JobScheduler(st).run("j4", boom, max_attempts=3)
    assert ok is False
    assert delays == [1.0, 2.0]
    assert st.get("j4") == "FAILED"


def test_cancelled_is_terminal():
    assert transition("PENDING", "CANCELLED") == "CANCELLED"
    with pytest.raises(InvalidTransition):
        transition("CANCELLED", "RUNNING")


def test_failed_must_go_through_retrying():
    with pytest.raises(InvalidTransition):
        transition("FAILED", "PENDING")
    assert transition("FAILED", "RETRYING") == "RETRYING"
    assert transition("RETRYING", "PENDING") == "PENDING"


def test_snapshot_isolated():
    st = InMemoryStore()
    st.set("a", "PENDING")
    snap = st.snapshot()
    snap["a"] = "SUCCEEDED"
    snap["ghost"] = "RUNNING"
    assert st.get("a") == "PENDING"
    assert st.get("ghost") == "PENDING"  # 不存在的 key 回落默认值


def test_retry_loop_via_store():
    st = InMemoryStore()

    calls = {"n": 0}

    def once():
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("first fails")

    ok, delays = JobScheduler(st).run("j5", once)
    assert ok is True and delays == [1.0]
