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

from server.wsdevice import wsdevice,basic_ws_info

from utils.lightlog import lightlog
log = lightlog(__name__)

import gettext
_ = gettext.gettext

__version__ = '1.0.0'

__success__ = 0
__error__ = 1
__warning__ = 2

class wssolver_info(basic_ws_info):
    """
        Websocket Solver information container
        Public basic_ws_info and SolverInfo
    """

class wssolver(wsdevice):
    """
        Websocket Solver Main Class
    """

    def __init__(self,_type : str, name : str, host : str, port : int, debug : bool, threaded : bool, ssl : dict) -> None:
        """
            Initializer function | 初始化\n
            Args:
                type : str # Type of camera
                name : str # Name of camera
                host : str # Host name
                port : int # Port number
                debug : bool # Debug mode
                ssl : {
                    "enable" : False # Enable SSL
                    "cert" : str # Certificate
                }
            Returns: None
            NOTE: This function override the parent function!
        """
        self.info = wssolver_info()

        self.info.host = host if host is not None else "127.0.0.1"
        self.info.port = port if port is not None else 5000
        self.info.debug = debug if debug is not None else False
        self.info.threaded = threaded if threaded is not None else True

        if self.start_server(self.info.host,self.info.port,False,True).get('status') != __success__:
            log.loge(_(""))
        self.info._name = name
        self.info._type = _type
        self.info.running = True
        
    def __del__(self) -> None:
        """Destructor"""
        if self.info._is_connected:
            self.disconnect()
        if self.info.running:
            self.stop_server()