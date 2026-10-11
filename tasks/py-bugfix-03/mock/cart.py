def add_item(item, cart=None):
    """把 item 加进购物车并返回。不传 cart 时应从空车开始。(mock 参考解)"""
    if cart is None:
        cart = []
    cart.append(item)
    return cart


def make_handlers(names):
    """返回一组无参函数,第 i 个被调用时返回 names[i]。(mock 参考解)"""
    return [lambda n=n: n for n in names]
