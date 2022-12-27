# coding=utf-8

"""

Copyright(c) 2022 Max Qian  <astroair.cn>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Library General Public
License version 3 as published by the Free Software Foundation.
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.
You should have received a copy of the GNU Library General Public License
along with this library; see the file COPYING.LIB.  If not, write to
the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301, USA.

"""

import selectors
import socket
from time import sleep

class TcpSocket(object):
    """
        TCP socket client interface
    """

    def __init__(self):
        self.lines = []
        self.buf = b''
        self.sock = None
        self.sel = None
        self.terminate = False

    def __del__(self):
        self.disconnect()

    def connect(self, hostname, port):
        self.sock = socket.socket()
        try:
            self.sock.connect((hostname, port))
            self.sock.setblocking(False)  # non-blocking
            self.sel = selectors.DefaultSelector()
            self.sel.register(self.sock, selectors.EVENT_READ)
        except Exception:
            self.sel = None
            self.sock = None
            raise

    def disconnect(self):
        if self.sel is not None:
            self.sel.unregister(self.sock)
            self.sel = None
        if self.sock is not None:
            self.sock.close()
            self.sock = None

    def terminate(self):
        self.terminate = True

    def read(self):
        while not self.lines:
            while True:
                if self.terminate:
                    return ''
                events = self.sel.select(0.5)
                if events:
                    break
            s = self.sock.recv(4096)
            i0 = 0
            i = i0
            while i < len(s):
                if s[i] == b'\r'[0] or s[i] == b'\n'[0]:
                    self.buf += s[i0 : i]
                    if self.buf:
                        self.lines.append(self.buf)
                        self.buf = b''
                    i += 1
                    i0 = i
                else:
                    i += 1
            self.buf += s[i0 : i]
        return self.lines.pop(0)

    def send(self, s):
        b = s.encode()
        totsent = 0
        while totsent < len(b):
            sent = self.sock.send(b[totsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totsent += sent

conn = TcpSocket()
conn.connect('127.0.0.1', 7624)
import threading
cond = threading.Condition()
conn.send("<getProperties version='%g'/>")
def is_number(s):
    try:  # 如果能运行float(s)语句，返回True（字符串s是浮点数）
        float(s)
        return True
    except ValueError:  # ValueError为Python的一种标准异常，表示"传入无效的参数"
        pass  # 如果引发了ValueError这种异常，不做任何事情（pass：不做任何事情，一般用做占位语句）
    try:
        import unicodedata  # 处理ASCii码的包
        unicodedata.numeric(s)  # 把一个表示数字的字符串转换为浮点数返回的函数
        return True
    except (TypeError, ValueError):
        pass
    return False
res = ""
is_gg = False
def a():
    global is_gg
    while not is_gg:
        if is_gg:
            break
        try:
            r = str(conn.read()).replace("b'","").replace("'","").replace("    ","").replace("\n","")
            title = r[0]
            if len(r) == 0:
                break
            if title is None:
                break
            if title == "<" or title == "O" or is_number(title):
                global res
                res = res + r
                print(r)
        except AttributeError:
            pass
try:
    b= threading.Thread(target=a)
    b.start()
    sleep(0.5)
    is_gg = True
    conn.disconnect()
except AttributeError:
    pass
import utils.xmltodict as xml
import json
print(json.dumps(xml.parser(res),indent=4))
