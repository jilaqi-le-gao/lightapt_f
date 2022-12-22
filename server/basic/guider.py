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

from server.basic.device import BasicDeviceAPI

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

class BasicGuiderInfo(object):
    """
        Basic Guider Information container
    """

    _is_connected = False
    _is_device_connected = False
    _is_looping = False
    _is_calibrating = False
    _is_dithering = False
    _is_guiding = False
    _is_settling = False

    _is_calibrated = False
    _is_selected = False
    _is_settled = False
    _is_starlost = False
    _is_starlocklost = False

    _can_cooling = False

    def get_dict(self) -> dict:
        """
            Return Guider Information in the dictionary format
        """

class BasicGuiderAPI(BasicDeviceAPI):
    """
        Basic Guider API
    """

    def start_guiding(self, params : dict) -> dict:
        """
            Start guiding | 开始导星
            Args:
                params:{

                }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    def abort_guiding(self) -> dict:
        """
            Abort guiding | 停止导星
            Returns:{
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    def start_calibration(self, params : dict) -> dict:
        """
            Start calibration | 开始校准
            Args:
                params:{

                }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : None
            }
        """
    
    def abort_calibration(self) -> dict:
        """
            Abort the calibration | 停止校准
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    def start_dither(self, params : dict) -> dict:
        """
            Start dithering | 开始抖动
            Args:
                params:{

                }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    def abort_dither(self) -> dict:
        """
            Abort dither | 停止抖动
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : None
            }
        """
