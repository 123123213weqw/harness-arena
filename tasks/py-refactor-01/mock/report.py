def render(shapes):
    return "\n".join(f"{s.describe()} area={s.area():.2f}" for s in shapes)
