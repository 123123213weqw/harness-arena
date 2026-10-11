from shapes import Circle, Square


def render(shapes):
    lines = []
    for s in shapes:
        if isinstance(s, Circle):
            lines.append(f"circle r={s.r:.2f} area={s.area():.2f}")
        elif isinstance(s, Square):
            lines.append(f"square a={s.a:.2f} area={s.area():.2f}")
        else:
            raise TypeError(f"unknown shape: {type(s).__name__}")
    return "\n".join(lines)
