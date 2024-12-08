class Request:
    """解析http请求"""

    method = None
    uri = None
    version = None
    body = ''
    headers = dict()
    __methods = dict.fromkeys((
        'GET', 'PUT', 'ICY',
        'COPY', 'HEAD', 'LOCK', 'MOVE', 'POLL', 'POST',
        'BCOPY', 'BMOVE', 'MKCOL', 'TRACE', 'LABEL', 'MERGE',
        'DELETE', 'SEARCH', 'UNLOCK', 'REPORT', 'UPDATE', 'NOTIFY',
        'BDELETE', 'CONNECT', 'OPTIONS', 'CHECKIN',
        'PROPFIND', 'CHECKOUT', 'CCM_POST',
        'SUBSCRIBE', 'PROPPATCH', 'BPROPFIND',
        'BPROPPATCH', 'UNCHECKOUT', 'MKACTIVITY',
        'MKWORKSPACE', 'UNSUBSCRIBE', 'RPC_CONNECT',
        'VERSION-CONTROL',
        'BASELINE-CONTROL'
    )) 
    __proto = 'HTTP'  

    def __init__(self, buf):
        self.parse(buf)

    def parse(self, buf):
        header_value = buf.strip().split("\r\n", 1)
        line = header_value[0]  # 方法、路径、协议
        head = header_value[1]  # 其余headers以及body

        # 解析请求行
        line = line.strip().split()
        if len(line) < 2:
            raise Exception("invalid request")
        if line[0] not in self.__methods:
            raise Exception("invalid request")
        if len(line) == 2:
            self.version = '0.9'
        else:
            if not line[2].startswith(self.__proto):
                raise Exception("invalid request")
            self.version = line[2][len(self.__proto)+1:]
        self.method = line[0]
        self.uri = line[1]  

        # 解析headers及body
        headers = head.strip().split("\r\n")
        if self.method.lower() == 'post':
            self.body = headers[-1:]
            headers = headers[:-1]
        for header in headers:  # headers
            if not header:
                break
            h = header.split(':', 1)
            if len(h[0].split()) != 1:
                raise Exception("invalid request")
            header_key = h[0].lower()  # header键
            header_value = len(h) != 1 and h[1].lstrip() or ''  # header值
            if header_key in self.headers:
                pass
            else:
                self.headers[header_key] = header_value
