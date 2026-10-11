def add_item(item, cart=[]):
    """把 item 加进购物车并返回。不传 cart 时应从空车开始。"""
    cart.append(item)
    return cart


def make_handlers(names):
    """返回一组无参函数,第 i 个被调用时返回 names[i](闭包捕获各自的元素)。"""
    return [lambda: n for n in names]
