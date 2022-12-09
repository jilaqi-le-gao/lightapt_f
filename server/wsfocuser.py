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


import gettext
import json
from driver.focuser.ascom import focuser as ascom
from libs.websocket import websocket_server
from utils.utility import switch , ThreadPool
from utils.lightlog import lightlog
log = lightlog(__name__)

_ = gettext.gettext


class wsfocuser_info(object):
    """
        Websocket Focuser information container
        Each Focuser has a standard one
    """

    _port = 5000
    _host = '127.0.0.1'

    _started = False
    _connected = False

    _timeout = 5
    _max_thread_num = 3
    _debug = False

    def get_dict(self) -> dict:
        """
            Returns in a dictionary format
        """
        return {
            "properties" : {
                "port" : self._port,
                "host" : self._host,
            },
            "status" : {
                "started": self._started,
                "connected": self._connected,
            },
            "settings": {
                "timeout": self._timeout,
                "max_thread_num": self._max_thread_num,
                "debug": self._debug
            }
        }


class wsfocuser(object):
    """
        Websocket Focuser Object

    """

    def __init__(self) -> None:
        """Constructor"""
        self._ws = None
        self._info = wsfocuser_info()
        self._device = None
        self._threadpool = ThreadPool(max_workers=3)

    def __del__(self) -> None:
        """Destructor"""
        
            
