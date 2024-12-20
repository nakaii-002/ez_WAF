import socket
from datetime import datetime
from threading import Thread
from config.conf import *
from parse import Request
from re_detect.detect import ReDetect
from ml_detect.detect import MlDetect
from db import log_block


def para_filter(r, addr):
    """检测web攻击，返回检测结果
        白名单优先级大于黑名单
    """
    # 白名单直接放行
    if WHITE_IP_SWITCH and addr[0] in WHITE_IP_LIST:
        return {"status": False}

    # uri黑白名单检测
    uri = r.uri.split('?')[0]
    if WHITE_URI_SWITCH and uri not in WHITE_URI_LIST:  # 开启uri白名单并且uri不在白名单中
        return {"status": True, "type": 'not-white-uri'}
    if uri in BLACK_URI_LIST and not WHITE_URI_SWITCH:  # 关闭uri白名单并且uri在黑名单中
        return {"status": True, "type": 'in-black-uri'}

    # 规则匹配
    det_data = ReDetect(r)
    result = det_data.run()

    # 随机森林预测
    if not result["status"]:
        ml_test = MlDetect(r)
        result = ml_test.run()

    return result


def connecting(conn, addr):
    """使用反向代理模式提供waf功能，阻止web攻击"""
    # 阻挡ip黑名单连接
    if addr[0] in BLACK_IP_LIST and ((WHITE_IP_SWITCH and addr[0] not in WHITE_IP_LIST) or (not WHITE_IP_SWITCH)):  # 白名单优先级大于黑名单
        conn.close()
        return

    # 接受客户端请求内容
    conn.setblocking(False)  # 设置非阻塞模式
    req = []
    while 1:
        try:
            buf = conn.recv(1024*2)
        except BlockingIOError:  # 无数据进入
            break
        req.append(buf.decode('utf-8'))
    req = ''.join(req)

    if not req:
        conn.close()
        return

    # 解析http请求，拦截攻击，记录拦截行为
    try:
        r = Request(req)
    except Exception as e:
        conn.close()
        print("Http parsing failed : " + str(e))
        return
    result = para_filter(r, addr)
    if result["status"]:
        conn.close()
        src_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_block(addr, r, result["type"], src_time)
        return

    # 向web服务器转发请求
    req = req.replace(WAF_IP, '{}:{}'.format(WEB_IP, WEB_PORT)) \
        .replace('keep-alive', 'close') \
        .replace('gzip', '').encode('utf-8')
    s1 = socket.socket()
    try:
        s1.connect((WEB_IP, WEB_PORT))
        s1.sendall(req)
    except Exception as e:
        print("Forwarding failed : " + str(e))
        s1.close()
        conn.close()
        return

    # 接收web服务器返回内容
    resp = b''
    while 1:
        try:
            buf = s1.recv(1024*2)
        except socket.timeout as e:
            print("Forwarding timeout : " + str(e))
            break
        resp += buf
        if not buf or (buf.startswith(b'WebSocket') and buf.endswith(b'\r\n\r\n')):
            break
    s1.close()

    # 向客户端转发web服务器内容
    resp = resp.replace(b'Content-Encoding: gzip\r\n', b'') \
        .replace(b'Transfer-Encoding: chunked\r\n', b'') \
        .replace(WEB_IP.encode('utf-8'), WAF_IP.encode('utf-8'))
    conn.send(resp)
    conn.close()


def run():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 8000))
    s.listen(5)
    try:
        while 1:
            conn, addr = s.accept()
            t = Thread(target=connecting, args=(conn, addr))
            t.start()
    finally:
        s.close()


if __name__ == '__main__':
    run()
