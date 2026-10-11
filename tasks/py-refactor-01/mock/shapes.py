import math


class Shape:
    def area(self):
        raise NotImplementedError

    def perimeter(self):
        raise NotImplementedError

    def describe(self):
        raise NotImplementedError


class Circle(Shape):
    def __init__(self, r):
        self.r = r

    def area(self):
        return math.pi * self.r ** 2

    def perimeter(self):
        return 2 * math.pi * self.r

    def describe(self):
        return f"circle r={self.r:.2f}"


class Square(Shape):
    def __init__(self, a):
        self.a = a

    def area(self):
        return self.a ** 2

    def perimeter(self):
        return 4 * self.a

    def describe(self):
        return f"square a={self.a:.2f}"


class Rect(Shape):
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def area(self):
        return self.w * self.h

    def perimeter(self):
        return 2 * (self.w + self.h)

    def describe(self):
        return f"rect w={self.w:.2f} h={self.h:.2f}"
