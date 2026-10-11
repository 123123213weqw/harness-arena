from cart import add_item, make_handlers


def test_add_item_fresh_default():
    assert add_item("a") == ["a"]
    assert add_item("b") == ["b"]


def test_add_item_explicit():
    assert add_item("x", ["seed"]) == ["seed", "x"]
    own = ["m"]
    add_item("n", own)
    assert own == ["m", "n"]


def test_handlers_capture_own():
    hs = make_handlers(["x", "y", "z"])
    assert [h() for h in hs] == ["x", "y", "z"]


def test_handlers_empty():
    assert make_handlers([]) == []
