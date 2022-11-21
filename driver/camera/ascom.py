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
the Free Software Foundation, Inctypes., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301, USA.

"""

from utils.lightlog import lightlog
from driver.basiccamera import (BasicCamera,CameraInfo)
from libs.alpyca.camera import (Camera,CameraStates,SensorType)
from libs.alpyca.exceptions import (DriverException,
                                    NotConnectedException,
                                    NotImplementedException)
log = lightlog(__name__)

import os
from time import sleep
from requests.exceptions import ConnectionError
from yaml import (safe_load,safe_dump)
import gettext
_ = gettext.gettext

states = {
    CameraStates.cameraIdle : 0 , 
    CameraStates.cameraExposing : 1 , 
    CameraStates.cameraDownload : 2 ,
    CameraStates.cameraReading:3 ,
    CameraStates.cameraWaiting:4 ,
    CameraStates.cameraError : 5}
sensor = {
    SensorType.CMYG : "cmyg",
    SensorType.CMYG2 : "cmyg2",
    SensorType.Color : "color",
    SensorType.LRGB : "LRGB",
    SensorType.Monochrome : "monochrome",
    SensorType.RGGB : "rggb",
}

class camera(BasicCamera):
    """ASCOM camera class"""

    def __init__(self) -> None:
        """Initialize camera"""
        self.info = CameraInfo()
        self.device = None
        log.log(_("Initialize ASCOM camera object successfully"))

    def __del__(self) -> None:
        """Delete camera object"""
        if self.info._is_connected:
            if self.disconnect({}).get("status") != "success":
                log.loge(_("Failed to disconnect from ASCOM Remote camera"))
                return
        self.device = None
        log.log(_("Delete ASCOM Remote camera object successfully"))

    def connect(self, params: dict) -> dict:
        """
            Connect to ASCOM camera | 连接ASCOM相机
            Args:
                params: {
                    "host" : str , default host is "127.0.0.1"
                    "port" : int # default port is 11111
                    "device_number" : int # default is 0
                }
            Returns:
                {
                    "status" : " "success","error","warning","debug"
                    "message" : "ASCOM camera is connected" # success
                                "Faild to connect to ASCOM camera" # error
                                "ASCOM camera is connected with warning" # warning
                                "Attempt to connect to ASCOM camera in debug mode" # debug
                    "params" : {
                        "name" : str # 
                        "info" : cameraInfo object
                    }
                }
        """
        # Check if the parameters are valid | 检查选项是否合法
        if not isinstance(params,dict):
            log.loge(_("Invalid parameters"))
            return self.return_message("error",_("Invalid parameters"),{})
        # Load information from the parameters | 读取参数
        host = params.get("host")
        port = params.get("port")
        device_number = params.get("device_number")
        # Check if the parameters is legal | 检查输入是否合法
        if not isinstance(host, str) or not isinstance(device_number,int) or not isinstance(port, int):
            log.loge(_("Invalid parameters when executing connect function"))
            return self.return_message("error",_("Invalid parameters when executing connect function"))
        ip_address = host + ":" + str(port)
        # Connect to ASCOM Remote Server | 连接ASCOMRemote服务器
        try:
            self.device = Camera(ip_address,device_number)
            self.device.Connected = True
            self.info._is_connected = True
        except DriverException as exception:
            log.loge(_(f"Failed to connect to camera , error: {exception}"))
            return self.return_message("error",_("Failed to connect to camera"),{"error": exception})
        except ConnectionError as exception:
            log.loge(_(f"Remote connection error: {exception}"))
            return self.return_message("error",_("Remote connection error"),{"error": exception})
        log.log(_("Connected to camera successfully"))
        # Update camera Infomation | 更新赤道仪信息
        res = self.update_config()
        if res.get("status") != "success":
            return res
        r = {
            "name" : self.info._name,
            "info" : res.get("params")
        }
        return self.return_message("success",_("Connected to camera successfully"),r)

    def disconnect(self, params: dict) -> dict:
        """
            Disconnect from ASCOM camera
            Args:
                params: {
                    "name" : str
                }
            Returns:
                {
                    "status" : " "success","error","warning","debug"
                    "message" : "Disconnect from ASCOM camera successfully" # success
                                "Faild to disconnect from ASCOM camera" # error
                                "ASCOM camera is disconnected with warning" # warning
                                "Attempting to disconnect from ASCOM camera in debug mode" # debug
                    "params" : {
                        "error" : error message # usually exception
                    }
                }
            Note : Must disconnect from camera when destory self !
        """
        log.log(_("Try to disconnect from ASCOM camera"))
        name = params.get("name")
        try:
            self.device.Connected = False
            self.info._is_connected = False
        except DriverException as e:
            log.loge(_("Failed to disconnect from camera , error : %s"),e)
            return self.return_message("error",_("Failed to disconnect from ASCOm camera"),{"error" : exception})
        except ConnectionError as exception:
            log.loge(_(f"Remote connection error: {exception}"))
            return self.return_message("error",_("Remote connection error"),{"error" : exception})
        log.log(_("Disconnect from ASCOM camera successfully"))
        return self.return_message("success",_("Disconnect from ASCOM camera successfully"),{})

    def update_config(self) -> dict:
        """
            Update configuration of ASCOM camera
            Returns:
                {
                    "status" : "success","error","warning","debug"
                    "message" : "Update configuration successfully" # success
                                "Faild to update configuration" # error
                                "ASCOM configuration is updated with warning" # warning
                                "Attempting to update configuration in debug mode" # debug
                    "params" : {
                        "info" : cameraInfo object (use get_dict())
                        "error" : error message # usually exception
                    }
                }
            Note : This function is usually run when initialize the camera
        """
        log.log(_("Update ASCOM camera configuration"))
        try:
            """Get basic information | 获取基础信息"""
            self.info._address = self.device.address
            self.info._name = self.device.Name
            self.info._api_version = self.device.api_version
            self.info._id = self.device._client_id
            self.info._description = self.device.Description
            """Get ability information | 获取能力信息 (即是否能够执行某些功能)"""
            self.info._can_abort_exposure = self.device.CanAbortExposure
            self.info._can_bin = self.device.CanAsymmetricBin
            self.info._can_fast_readout = self.device.CanFastReadout
            self.info._can_get_coolpower = self.device.CanGetCoolerPower
            self.info._can_guiding = self.device.CanPulseGuide
            self.info._can_set_temperature = self.device.CanSetCCDTemperature
            self.info._can_stop_exposure = self.device.CanStopExposure
            """Get property infomation | 获取配置信息"""
            self.info._height = self.device.CameraYSize
            self.info._width = self.device.CameraXSize
            self.info._max_exposure = self.device.ExposureMax
            self.info._min_exposure = self.device.ExposureMin
            self.info._resolution_exposure = self.device.ExposureResolution
            self.info._full_capacit = self.device.FullWellCapacity
            if self.info._can_set_temperature:
                self.info._highest_temperature = self.device.HeatSinkTemperature
            else:
                self.info._highest_temperature = -114115
            self.info._max_adu = self.device.MaxADU
            self.info._max_bin_x = self.device.MaxBinX
            self.info._max_bin_y = self.device.MaxBinY
            self.info._subframe_x = self.device.NumX
            self.info._subframe_y = self.device.NumY
            self.info._pixel_height = self.device.PixelSizeY
            self.info._pixel_width = self.device.PixelSizeX
            self.info._readout_mode = self.device.ReadoutMode
            self.info._readout_modes = self.device.ReadoutModes
            self.info._sensor_name = self.device.SensorName
            self.info._sensor_type = sensor.get(self.device.SensorType)
            self.info._start_x = self.device.StartX
            self.info._start_y = self.device.StartY
            if not self.info._sensor_type == "monochrome":
                self.info._bayer_offset_x = self.device.BayerOffsetX
                self.info._bayer_offset_y = self.device.BayerOffsetY
            else:
                self.info._bayer_offset_x = -1
                self.info._bayer_offset_y = -1
            """Get current information"""
            if self.info._can_get_coolpower:
                self.info._cooling_power = self.device.CoolerPower
            else:
                self.info._cooling_power = 0
            self.info._temperature = self.device.CCDTemperature
            if not self.info._is_first_image:
                self.info._last_exposure = self.device.LastExposureDuration  
                self.info._last_exposure_time = self.device.LastExposureStartTime
            else:
                self.info._last_exposure = -1         
                self.info._last_exposure_time = -1
            self.info._bin_x = self.device.BinX
            self.info._bin_y = self.device.BinY
            self.info._percent_complete = self.device.PercentCompleted
            try:
                self.info._gain = self.device.Gain
                self.info._gains = self.device.Gains
                self.info._can_gain = True
            except NotImplementedException as exception:
                self.info._can_gain = False
            if self.info._can_gain:
                self.info._max_gain = self.device.GainMax
                self.info._min_gain = self.device.GainMin
            else:
                self.info._max_gain = -1
                self.info._min_gain = -1
            """try:
                self.info._offsets = self.device.Offsets
                self.info._can_offset = True
            except NotConnectedException as exception:
                self.info._can_offset = False
            if self.info._can_offset:
                self.info._max_offset = self.device.OffsetMax
                self.info._min_offset = self.device.OffsetMin
            else:
                self.info._max_offset = -1
                self.info._min_offset = -1"""
            """Get status information | 获取相机状态信息"""
            self.info._is_cooling = self.device.CoolerOn
            if self.info._can_guiding:
                self.info._is_guiding = self.device.IsPulseGuiding
            if self.info._can_fast_readout:
                self.info._is_fastreadout = self.device.FastReadout
            self.info._is_exposure = states.get(self.device.CameraState)
            self.info._is_imgready = self.device.ImageReady

            self.info._config_file = self.device.Name
        #except NotImplementedException as exception:
        #    log.loge(_(f"Property could not be read from camera , error : {exception}"))
        #    return self.return_message("error",_("Property could not be read from camera"))
        except NotConnectedException as exception:
            log.loge(_("No camera connected , please connect to camera before run update_config()"))
            return self.return_message("error", _("No camera connected"),{"error" : exception})
        except DriverException as exception:
            log.loge(_("camera driver error , when run update_config()"))
            return self.return_message("error", _("camera driver error"),{"error" : exception})
        except ConnectionError as exception:
            log.loge(_("Remote server connection error, when run update_config()"))
            return self.return_message("error",_("Remote connection error"),{"error" : exception})
        
        log.log(_("Update camera configuration successfully"))
        return self.return_message("success", _("Update camera configuration successfully"),self.info.get_dict())

    def load_config(self, params: dict) -> dict:
        """
            Load configuration from file | 从文件中加载配置
            Args:
                {
                    "filename": filename,
                    "path": path,
                }
            Return:
                {
                    "status": "success","error","warning","debug"
                    "message" : str
                    "params" : configuration load from file
                }
        """
        path = os.path.join(params.get("path"), params.get("filename"))
        if not os.path.isfile(path):
            log.loge(_("Faild to load configuration file %(path)s"))
            return self.return_message("error", _("Faild to load configuration file %(path)"),{})
        with open(path, mode = 'r', encoding="utf-8") as file:
            config = safe_load(file)

    def save_config(self) -> dict:
        """
            Save the configuration file | 保存配置文件
            Return:
                {
                    "status" : "success","error","warning","debug"
                    "message" : str
                    "params" : {
                        "error" : exception
                    }
                }
        """
        _p = os.path.join
        try:
            if self.info._config_file.find("yaml") == -1:
                self.info._config_file += ".yaml"
            if not os.path.exists("config"):
                os.mkdir("config")
            if not os.path.exists(_p("config","device")):
                os.mkdir(_p("config","device"))
            folder = _p("config",_p("device","camera"))
            if not os.path.exists(folder):
                os.mkdir(folder)
        except FileNotFoundError as exception:
            """FileNotFoundError"""
        path = _p(_p(_p(_p(os.getcwd(),"config"),"device"),"camera"),self.info._config_file)
        try:
            with open(path,mode="w+",encoding="utf-8") as file:
                safe_dump(self.info.get_dict(), file)
        except IOError as exception:
            log.loge(_(f"Faild to save configuration file {path} error : {exception}"))
            return self.return_message("error", _("Faild to save configuration file %(path)"),self.info.get_dict())
        log.log(_("Save configuration file successfully"))
        return self.return_message("success", _("Save configuration file successfully"),self.info.get_dict())