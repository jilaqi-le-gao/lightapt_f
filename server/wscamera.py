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

from utils.lightlog import lightlog
from driver.basiccamera import BasicCamera,CameraInfo
from driver.camera.ascom import camera as ascom

from flask_socketio import emit,SocketIO

import gettext
_ = gettext.gettext

log = lightlog(__name__)

class wscamera(BasicCamera):
    """Websocket camera class"""

    def __init__(self) -> None:
        super().__init__()
        self.info = CameraInfo()
        self.device = None

    def __del__(self) -> None:
        super().__del__()

    def connect(self,_ws : SocketIO, params: dict) -> dict:
        """
        Connect to the camera | 连接相机
        Args:
            params (dict): camera parameters
            {
                "name" : str # Camera name
                "count" : int # Number of cameras
                # Only for ASCOM and INDI
                "port" : int # Port number
                "ip" : str # IP address
            }
        Returns:
            dict: camera parameters
            {
                "status" : "success","error","warning","debug"
                "message" : "Camera connection established successfully" # success
                            "Faild to connect to the camera" # error
                            "No camera connected" # warning
                            "No camera connected" # debug
                "params" : {
                    "name" : str # Camera name
                    "info" : CameraInfo object
                }
            }

        """
        res = self.device.connect(params)
        status = None
        if res.get("status") != "success":
            log.loge(_(f"Error connecting to camera , error : {res.get('message')}"))
            status = "error"
        message = {
            "method" : ""
        }
        _ws.emit(message,namespace="lightapt")

    def disconnect(self, params: dict) -> dict:
        """
            Disconnect from the camera | 与相机断开连接
            Args:
                params (dict): None
            Returns:
                {
                    "status" : "success","error","warning","debug"
                    "message" : str
                    "params" : {
                        "error" : error message
                        'warning" : warning message
                        'debug' : debug message
                    }
                }
            Note : This function must be called before shutdown the server
        """

    def update_config(self) -> dict:
        """
            Update camera configuration | 更新相机信息
            Args:
                None
            Returns:
                {
                    "status" : "success","error","warning","debug"
                    "message" : str
                    "params" : {
                        "info" : CameraInfo object
                    }
                }
            Note : This function should be called when after connection is established
        """


