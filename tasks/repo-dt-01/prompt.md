当前目录 vendor 了真实日期解析库 python-dateutil 的旧版本(`dateutil/`,parser.py 2000+ 行)。用户报告:

```python
from dateutil.parser import parse
parse('shouldfail')   # 无法解析的字符串
# 抛 TypeError: cannot unpack non-iterable NoneType object —— 错误类型违反 API 契约
```

契约(与官方最终版一致):无法解析的字符串必须抛 `ValueError("unknown string format")`。

根因线索:`_parse()` 的**成功**路径末尾返回二元组 `(res, skipped_tokens)`,但多处**失败**路径提前 `return None`(裸单值);`parse()` 无条件做 `res, skipped_tokens = self._parse(...)` 二元组解包,于是失败路径炸成 TypeError。官方最终版本的解法是让 `_parse()` 的失败路径也统一返回二元组(如 `return None, None`),由 `parse()` 里既有的 `if res is None: raise ValueError(...)` 兜底。

要求:

1. 修复后 `parse('shouldfail')` 抛 `ValueError`;
2. 正常解析(含 `fuzzy=True`)返回单个 datetime,`fuzzy_with_tokens=True` 返回 `(datetime, tokens)` 元组,既有正确行为不得改变;
3. 不得用 try/except 把 TypeError 转成 ValueError 这种掩盖式修法——要从返回契约上修。

完成后自测以上场景再结束。
