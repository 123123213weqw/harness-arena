import math
from pathlib import Path

from report import render
from shapes import Circle, Rect, Shape, Square


def test_old_output_unchanged():
    assert render([Circle(1), Square(2)]) == (
        "circle r=1.00 area=3.14\nsquare a=2.00 area=4.00"
    )


def test_rect_renders():
    assert render([Rect(2, 3)]) == "rect w=2.00 h=3.00 area=6.00"
    assert render([]) == ""


def test_mixed():
    out = render([Rect(2, 3), Circle(1), Square(2)])
    assert out == (
        "rect w=2.00 h=3.00 area=6.00\ncircle r=1.00 area=3.14"
        "\nsquare a=2.00 area=4.00"
    )


def test_perimeters():
    assert abs(Circle(1).perimeter() - 2 * math.pi) < 1e-9
    assert Square(2).perimeter() == 8
    assert Rect(2, 3).perimeter() == 10


def test_hierarchy():
    assert isinstance(Rect(1, 1), Shape)
    assert isinstance(Circle(1), Shape)
    assert isinstance(Square(1), Shape)


def test_render_is_polymorphic():
    src = Path("report.py").read_text(encoding="utf-8")
    assert "isinstance" not in src, "render 不得再用 isinstance 分发"
    for name in ("Circle", "Square", "Rect"):
        assert name not in src, f"render 不得引用具体形状 {name}"

    class Blob(Shape):
        def __init__(self, w):
            self.w = w

        def area(self):
            return self.w ** 3

        def perimeter(self):
            return 6 * self.w

        def describe(self):
            return f"blob w={self.w:.2f}"

    assert render([Blob(2)]) == "blob w=2.00 area=8.00"
