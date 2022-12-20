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

from server.basic.camera import BasicCameraAPI,BasicCameraInfo

from utils.lightlog import lightlog
log = lightlog(__name__)

import gettext
_ = gettext.gettext

import ctypes as c

class ASICameraAPI(BasicCameraAPI):
    """
        ASI Camera API via ASICamera2.dll/so
    """

    def __init__(self) -> None:
        self.info = BasicCameraInfo()
        self.device = None
        self.info._is_connected = False
    
    def __del__(self) -> None:
        if self.info._is_connected:
            self.disconnect()

    def init_dll(self) -> None:
        """
            Initialize the dll library | 加载dll
            Args: None
            Returns: None
        """
        self.device = c.cdll.LoadLibrary()

        self.device.ASIGetNumOfConnectedCameras.argtypes = []
        self.device.ASIGetNumOfConnectedCameras.restype = c.c_int
        
    def connect(self, params: dict) -> dict:
        """
            Connect to the ASI camera | 连接ASI相机
            Args:
                params:{
                    "name" : str,
                }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : {
                    "info" : BasicCameraInfo object
                }
            }
            NOTE : Name which is given should be formatted
        """
        if self.info._is_connected:
            log.logw(_("Camera is connected , please do not execute connect command again"))
            return log.return_warning(_("Camera is connected"),{})
        if self.device is not None:
            log.logw(_("Each server can only connect to one device at a time"))
            return log.return_warning(_("Each server can only connect to one device at a time"),{})
        name = params.get("name")
        if name is None:
            log.loge(_("Camera name is required,but now get a NoneType object"))
            return log.return_error(_("Camera name is required,but now get a NoneType object"),{})
        
    