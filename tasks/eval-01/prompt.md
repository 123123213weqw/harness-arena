在当前目录创建 `profile.html`:一个静态个人主页,**只用结构性要求判定**(不看样式美观):

1. `<!DOCTYPE html>` 开头,根元素 `<html lang="zh-CN">`;
2. `<head>` 含 `<meta charset="utf-8">`、`<meta name="viewport" content="width=device-width, initial-scale=1">`、`<title>` 文本恰好为 `个人主页`;
3. `<body>` 内按顺序包含:
   - `<header>` 里一个 `<h1>`,文本恰好为 `张三的个人主页`;
   - `<nav>` 里一个 `<ul>`,其 `<li>` 子项恰好 3 个,每个含一个带 `href` 属性的 `<a>`;
   - `<main>` 里一个 `<section>`(带非空 `id` 属性),含一个 `<h2>` 和至少一段 `<p>`;
   - 一个 `<form>`(带 `action` 属性),内含一个 `<label for="email">`、一个 `<input type="email" id="email" name="email">`、一个 `<button type="submit">`;
   - `<footer>` 含文本 `2026`;
4. `<img>`(若有)必须带非空 `alt`;
5. 全文不得出现 `<script>` 或 `style=`(内联样式)。

判定脚本只做结构检查(HTML 解析器遍历),与缩进/换行/属性顺序无关。完成后自查再结束。
