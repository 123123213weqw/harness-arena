当前目录 vendor 了真实流处理库 more-itertools(`more_itertools/`,5600+ 行)。用户报告一个隐蔽的 bug:`one()` 与 `only()` 支持 `too_short` / `too_long` 自定义异常参数,但当传入的**异常实例为 falsy**(如自定义了 `__bool__` 返回 False 的异常类实例)时,会被当作「没传」而忽略,转而抛默认的 `ValueError`:

```python
class FalsyError(Exception):
    def __bool__(self):
        return False

one([1, 2, 3], too_long=FalsyError('boom'))   # 当前抛 ValueError(错);应抛 FalsyError
```

根因:实现里用了 `raise too_long or ValueError(msg)` 这类**把异常实例当布尔**的写法。请修复 `more.py` 中 `one()` 与 `only()` 两处,要求:

1. 只要 `too_short`/`too_long` 参数**不为 None**(哪怕实例 falsy)就抛它;为 None 时抛默认 ValueError,消息语义不变;
2. 不使用 try/except 或哈希等迂回手段,直接从条件判断上修;
3. 其他函数与默认行为(消息文本)不得变化。

不得改动库中其他函数。完成后自测(falsy 异常、truthy 异常、默认值三类)再结束。
