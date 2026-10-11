当前目录是一个小形状库:`shapes.py`(Circle/Square,各带 `area()`)与 `report.py`(`render()` 用 `isinstance` 链分发格式)。请重构:

1. 在 `shapes.py` 引入共同基类 `Shape`,声明 `area()`、`perimeter()` 与 `describe()`(返回不含面积部分的描述前缀,如 `circle r=1.00`),Circle/Square 继承实现;`describe()` 中数值用两位小数格式化;
2. 新增 `Rect(w, h)`:`area() == w*h`,`perimeter() == 2*(w+h)`,`describe()` 返回 `rect w=.. h=..`;
3. `report.py` 的 `render()` 改为纯多态:每行 `f"{s.describe()} area={s.area():.2f}"`,**不得再出现 `isinstance` 或任何具体形状类名**(Circle/Square/Rect 之外的形状也应能渲染);
4. **输出必须与重构前完全一致**:`render([Circle(1), Square(2)])` 仍是 `circle r=1.00 area=3.14\nsquare a=2.00 area=4.00`;Rect(2,3) 渲染为 `rect w=2.00 h=3.00 area=6.00`;
5. `perimeter()`:Circle(1) 为 `2πr`,Square(2) 为 `8`,Rect(2,3) 为 `10`。

保持模块路径与既有函数签名不变。完成后自测再结束。
