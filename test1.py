import selectors
import socket

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

tcp = TcpSocket()
tcp.connect("127.0.0.1",7624)
tcp.send("<getProperties version='1.7' device='CCD Simulator'/>")
while True:
    print(tcp.read())