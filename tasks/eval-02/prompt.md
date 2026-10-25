实现当前目录 `httpreq.py` 的 `parse_request(data: bytes) -> dict`:解析 HTTP/1.x 请求的**首部部分**(RFC 7230 子集),返回:

```python
{"method": str, "target": str, "version": str,
 "headers": {小写头名: 值(两侧 OWS 已剥)}}
```

规则:

1. `data` 按 `\r\n\r\n` 分首部与(忽略的)实体;**至少要有一对 CRLF CRLF**,否则 `ValueError("incomplete")`;
2. 请求行:方法、目标、版本三个 token,**以单个空格分隔**;方法必须全大写字母且无空格;版本必须是 `HTTP/1.0` 或 `HTTP/1.1`(其他 → `ValueError`);tab 分隔请求行视为非法;
3. 头部行:`名字: OWS 值`——**以第一个冒号分隔**;名字不得为空、不得含空白或 `:`;**头部值可以合法包含冒号**(如 `Referer: http://x`);**头名大小写不敏感**(输出键为小写);同名头多次出现时**以 `, ` 连接**保留出现顺序;值两侧的空格/tab 剥除,内部空白保留;
4. 首部行若以空格或 tab 开头(过时折行 obs-fold)→ `ValueError("obs-fold")`;
5. 空行之后的部分全部忽略;`data` 解码为 latin-1 处理;任何结构不合 → `ValueError`。

保持签名;完成后自测(含大小写、重复头、折行、tab 值)再结束。
