"""HTTP/1.x 请求首部解析(RFC 7230 子集)。"""


def parse_request(data: bytes) -> dict:
    """解析请求首部,返回 method/target/version/headers(键小写)。"""
    raise NotImplementedError
