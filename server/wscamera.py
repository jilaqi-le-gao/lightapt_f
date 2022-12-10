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

from driver.basiccamera import CameraInfo
from server.wsdevice import wsdevice,basic_ws_info
from utils.utility import switch, ThreadPool
from utils.lightlog import lightlog
log = lightlog(__name__)

import gettext
_ = gettext.gettext

class wscamera_info(basic_ws_info,CameraInfo):
    """
        Websocket camera information container
        Public basic_ws_info and CameraInfo
    """

    _type : str
    _name : str

    def get_dict(self) -> dict:
        """Return camera infomation in a dictionary"""
        r = {
            "ws" : {
                "host" : self.host,
                "port" : self.port,
                "debug" : self.debug,
                "threaded" : self.threaded,
                "running" : self.running,
                "connected" : self.connected,
                "name" : self._name,
                "type" : self._type
            },
            "address": self._address,
            "api_version" : self._api_version,
            "description": self._description,
            "id": self._id,
            "timeout" : self._timeout,
            "ability" : {
                "can_stop_exposure" : self._can_stop_exposure,
                "can_abort_exposure" : self._can_abort_exposure,
                "can_guiding" : self._can_guiding,
                "can_binning" : self._can_bin,
                "can_gain" : self._can_gain,
                "can_offset" : self._can_offset,
                "can_set_temperature" : self._can_set_temperature,
                "can_get_coolpower" : self._can_get_coolpower,
                "can_fast_readout" : self._can_fast_readout,
                "has_shutter" : self._has_shutter
            },
            "properties" : {
                "bayer_offset_x" : self._bayer_offset_x,
                "bayer_offset_y" : self._bayer_offset_y,
                "height" : self._height,
                "width" : self._width,
                "max_expansion" : self._max_exposure,
                "min_expansion" : self._min_exposure,
                "resolution_exposure" : self._resolution_exposure,
                "full_capacit" : self._full_capacit,
                "max_gain" : self._max_gain,
                "min_gain" : self._min_gain,
                "max_offset" : self._max_offset,
                "min_offset" : self._min_offset,
                "highest_temperature" : self._highest_temperature,
                "last_exposure_time" : self._last_exposure_time,
                "max_adu" : self._max_adu,
                "max_bin_x" : self._max_bin_x,
                "max_bin_y" : self._max_bin_y,
                "subframe_x" : self._subframe_x,
                "subframe_y" : self._subframe_y,
                "pixel_height" : self._pixel_height,
                "pixel_width" : self._pixel_width,
                "readout_mode" : self._readout_mode,
                "readout_modes" : self._readout_modes,
                "sensor_name" : self._sensor_name,
                "sensor_type" : self._sensor_type,
                "start_x" : self._start_x,
                "start_y" : self._start_y,
            },
            "current" : {
                "cooling_power" : self._cooling_power,
                "temperature" : self._temperature,
                "last_exposure" : self._last_exposure,
                "gain" : self._gain,
                "offset" : self._offset,
                "gains" : self._gains,
                "offsets" : self._offsets,
                "bin_x" : self._bin_x,
                "bin_y" : self._bin_y,
                "percent_complete" : self._percent_complete
            },
            "status" : {
                "exposure" : self._is_exposure,
                "video" : self._is_video,
                "guiding" : self._is_guiding,
                "cooling" : self._is_cooling,
                "fastreadout" : self._is_fastreadout,
                "imgready" : self._is_imgready,
            }
        }
        return r

class wscamera(wsdevice):
    """
        Websocket Camera Main Class
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
        self.info = wscamera_info()

        self.info.host = host if host is not None else "127.0.0.1"
        self.info.port = port if port is not None else 5000
        self.info.debug = debug if debug is not None else False
        self.info.threaded = threaded if threaded is not None else True

        if self.start_server(self.info.host,self.info.port,False,True) == "success":
            pass
        self.info._name = name
        self.info._type = _type
        self.info.running = True
        
    def __del__(self) -> None:
        """Destructor"""
        if self.info.running:
            self.stop_server()

    def start_server(self, host : str, port : int, debug = False, ssl = {}) -> dict:
        """Public from parent class"""
        return super().start_server(host, port, debug, ssl)

    def stop_server(self) -> dict:
        """Public from parent class"""
        if self.info.running:
            self.info.running = False
            log.log(_("Shutting down server ... please wait for a moment"))
            return super().stop_server()

    def restart_server(self) -> dict:
        """Public from parent class"""
        return super().restart_server()

    # #################################################################
    #
    # Following methods have no return value and just send results to client
    #
    # #################################################################

    def remote_dashboard_setup(self,params : dict) -> None:
        """
            Remote dashboard setup function | 建立连接并且初始化客户端
            Args : {
                "status": "success","error","warning","debug",
                "message" : str,
                "params" : {
                    "name" : str # name of the camera
                    "type" : str # type of the camera
                    "info" : CameraInfo object # information about the camera
                }
            }
            Returns : None
            ClientArgs : None
            ServerResult : {
                "event" : "RemoteDashboardSetup",
                "id" : int # just a random number,
                status" : "success","error","warning","debug",
                "message" : str,
                "params" : {
                    "name" : str # name of the camera
                    "type" : str # type of the camera
                    "info" : CameraInfo object # information about the camera
                }
            
            NOTE : This function should be called when connection with camera is established
        """

    # #################################################################
    #
    # The following functions are used to communicate with the hardware driver
    #
    # #################################################################

    def connect(self,params : dict) -> dict:
        """
            Connect to the camera | 连接相机
            Args : {
                "name" : str # name of the camera
                "type" : str # type of the camera
            }
            Returns : {
                "status" : "success","error","warning","debug",
                "message" : str,
                "params" : {
                    "name" : str # name of the camera
                    "type" : str # type of the camera
                    "info" : CameraInfo object # information about the camera
                }
            }
        """

    def disconnect(self) -> dict:
        """
            Disconnect from the camera | 与相机断开连接
            Args : None
            Returns : {
                "status" : "success","error","warning","debug",
                "message" : str,
                "params" : None
            }
        """

    def update_config(self) -> dict:
        """
            Update the configuration of the camera | 更新相机信息
            Args : None
            Returns : {
                "status" : "success","error","warning","debug",
                "message" : str,
                "params" : {
                    "info" : CameraInfo object
                }
            }
        """