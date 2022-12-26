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
from libs.alpyca.camera import Camera,CameraStates,SensorType,ImageArrayElementTypes
from libs.alpyca.exceptions import (DriverException,
                                        NotConnectedException,
                                        NotImplementedException,
                                        InvalidValueException,
                                        InvalidOperationException)
from server.driver.camera.exception import AscomCameraError as error
from server.driver.camera.exception import AscomCameraSuccess as success
from server.driver.camera.exception import AscomCameraWarning as warning

from utils.lightlog import lightlog
log = lightlog(__name__)

import gettext
_ = gettext.gettext

from time import sleep
from datetime import datetime
from os import path,mkdir,getcwd
from json import dumps,JSONDecodeError
import numpy as np
import astropy.io.fits as fits
from io import BytesIO
from base64 import b64encode
from requests.exceptions import ConnectionError
from sys import _getframe

CameraState = {
    CameraStates.cameraIdle : 0 , 
    CameraStates.cameraExposing : 1 , 
    CameraStates.cameraDownload : 2 ,
    CameraStates.cameraReading:3 ,
    CameraStates.cameraWaiting:4 ,
    CameraStates.cameraError : 5
}

Sensor = {
    SensorType.CMYG : "cmyg",
    SensorType.CMYG2 : "cmyg2",
    SensorType.Color : "color",
    SensorType.LRGB : "LRGB",
    SensorType.Monochrome : "monochrome",
    SensorType.RGGB : "rggb",
}

class AscomCameraAPI(BasicCameraAPI):
    """
        Ascom Camera API for LightAPT server.
        Communication with ASCOM via Alpyca.
        LightAPT server has already built in alpyca.
        You can use this API to control camera.
        NOTE : To use this , you must run ASCOM Remote too.
        https://github.com/ASCOMInitiative/alpyca
        https://github.com/ASCOMInitiative/ASCOMRemote
    """

    def __init__(self) -> None:
        self.info = BasicCameraInfo()
        self.device = None
        self.info._is_connected = False
        self.info._percent_complete = 0

    def __del__(self) -> None:
        if self.info._is_connected:
            self.disconnect()

    # #################################################################
    #
    # Public methods from BasicCameraAPI
    #
    # #################################################################
    
    def connect(self, params: dict) -> dict:
        """
            Connect to ASCOM camera | 连接ASCOM相机
            Args: {
                "host": "127.0.0.1",
                "port": 8888,
                "device_number" : int # default is 0
            }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : {
                    "info" : BasicCameraInfo object
                }
            }
        """
        if self.info._is_connected:
            log.logw(_(f"Camera is connected , please do not execute {_getframe().f_code.co_name} command again"))
            return log.return_warning(_("Camera is connected"),{})
        if self.device is not None:
            log.logw(error.OneDevice)
            return log.return_warning(error.OneDevice,{"error":error.OneDevice})
        host = params.get('host')
        port = params.get('port')
        device_number = params.get('device_number')
        if host is None:
            log.logw(error.NoHostValue)
            host = "127.0.0.1"
        if port is None:
            log.logw(error.NoPortValue)
            port = 11111
        if device_number is None:
            log.logw(error.NoDeviceNumber)
            device_number = 0
        try:
            self.device = Camera(host + ":" + str(port), device_number)
            self.device.Connected = True
        except DriverException as e:
            log.loge(_(f"Faild to connect to device on {host}:{port}"))
            return log.return_error(_(f"Failed to connect to device on {host}:{port}"))
        except ConnectionError as e:
            log.loge(_(f"Network error while connecting to camera , error : {e}"))
            return log.return_error(_("Network error while connecting to camera"),{"error" : e})
        log.log(_("Connected to device successfully"))
        self.info._is_connected = True
        self.info._type = "ascom"
        res = self.get_configration()
        if res.get('status') != 0:
            return log.return_error(_(f"Failed tp load camera configuration"),{})
        return log.return_success(_("Connect to camera successfully"),{"info":res.get("info")})

    def disconnect(self) -> dict:
        """
            Disconnect from ASCOM camera
            Args: None
            Returns: {
                "status" : int,
                "message" : str,
                "params" : None
            }
            NOTE : This function must be called before destory all server
        """
        if not self.info._is_connected or self.device is None:
            log.logw(_(f"{error.NotConnected} , please do not execute {_getframe().f_code.co_name} command"))
            return log.return_warning(_(error.NotConnected),{})
        try:
            self.device.Connected = False
        except DriverException as e:
            log.loge(_(f"Faild to disconnect from device , error : {e}"))
            return log.return_error(error.DriverError,{"error" : e})
        except ConnectionError as e:
            log.loge(_(f"Network error while disconnecting from camera, error : {e}"))
            return log.return_error(error.NetworkError,{"error" : e})
        self.device = None
        self.info._is_connected = False
        log.log(_("Disconnected from camera successfully"))
        return log.return_success(_("Disconnect from camera successfully"),{"params":None})

    def reconnect(self) -> dict:
        """
            Reconnect to ASCOM camera | 重连ASCOM相机
            Args: None
            Returns: {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """
        if self.device is None or not self.info._is_connected:
            log.logw(_(f"{error.NotConnected} , please do not execute {_getframe().f_code.co_name} command"))
            return log.return_warning(_(error.NotConnected),{}) 
        try:
            self.device.Connected = False
            sleep(1)
            self.device.Connected = True
        except DriverException as e:
            log.loge(_(f"Faild to reconnect to device, error : {e}"))
            return log.return_error(_(f"Failed to reconnect to device"),{"error" : e})
        except ConnectionError as e:
            log.loge(_(f"Network error while reconnecting to camera, error : {e}"))
            return log.return_error(error.NetworkError,{"error" : e})
        log.log(success.ReconnectSuccess)
        self.info._is_connected = True
        return log.return_success(success.ReconnectSuccess,{})

    def scanning(self) -> dict:
        """
            Scan ASCOM camera | 扫描ASCOM相机
            Args: None
            Returns: {
                "status" : int,
                "message" : str,
                "params" : {
                    "camera" : list
                }
            }
        """
        if self.device is not None and self.info._is_connected:
            log.logw(warning.DisconnectBeforeScanning)
            return log.return_warning(warning.DisconnectBeforeScanning,{"warning":warning.DisconnectBeforeScanning})
        l = []
        log.log(_(f"Scanning camera : {l}"))
        log.log(success.ScanningSuccess)
        return log.return_success(success.ScanningSuccess,{"camera":l})

    def polling(self) -> dict:
        """
            Polling camera information | 刷新相机信息
            Args: None
            Returns: {
                "status" : int,
                "message" : str,
                "params" : {
                    "info" : BasicCameraInfo object
                }
            }
        """
        if self.device is None or not self.info._is_connected:
            log.logw(_(f"{error.NotConnected} , please do not execute polling command"))
            return log.return_warning(_(error.NotConnected),{})
        res = self.info.get_dict()
        log.logd(_(f"New camera info : {res}"))
        log.log(success.PollingSuccess)
        return log.return_success(success.PollingSuccess,{"info":res})

    def get_configration(self) -> dict:
        """
            Get camera infomation | 获取相机信息
            Args: None
            Returns: {
                "status" : int,
                "message" : str,
                "params" : {
                    "info" : BasicCameraInfo object
                }
            }
        """
        if self.device is None or not self.info._is_connected:
            log.logw(_(f"{error.NotConnected}, please do not execute {_getframe().f_code.co_name} command"))
            return log.return_warning(_(error.NotConnected),{})
        try:
            self.info._name = self.device.Name
            log.logd(_(f"Camera name : {self.info._name}"))
            self.info._id = self.device._client_id
            log.logd(_(f"Camera ID : {self.info._id}"))
            self.info._description = self.device.Description
            log.logd(_(f"Camera description : {self.info._description}"))
            self.info._ipaddress = self.device.address
            log.logd(_(f"Camera IP address : {self.info._ipaddress}"))
            self.info._api_version = self.device.api_version
            log.logd(_(f"Camera API version : {self.info._api_version}"))

            self.info._can_binning = self.device.CanAsymmetricBin
            log.logd(_(f"Can camera set binning mode : {self.info._can_binning}"))
            self.info._binning = [self.device.BinX, self.device.BinY]
            log.logd(_(f"Camera current binning mode : {self.info._binning}"))

            self.info._can_cooling = self.device.CanSetCCDTemperature
            log.logd(_(f"Can camera set cooling : {self.info._can_cooling}"))
            self.info._can_get_coolpower = self.device.CanGetCoolerPower
            log.logd(_(f"Can camera get cooling power : {self.info._can_get_coolpower}"))
            if self.info._can_cooling:
                try:
                    self.info._temperature = self.device.CCDTemperature
                except InvalidValueException as e:
                    log.logd(error.CanNotGetTemperature)
            if self.info._can_get_coolpower:
                try:
                    self.info._cool_power = self.device.CoolerPower
                except InvalidValueException as e:
                    log.logd(error.CanNotGetPower)
            try:
                self.info._gain = self.device.Gain
                log.logd(_(f"Camera current gain : {self.info._gain}"))
                self.info._max_gain = self.device.GainMax
                log.logd(_(f"Camera max gain : {self.info._max_gain}"))
                self.info._min_gain = self.device.GainMin
                log.logd(_(f"Camera min gain : {self.info._min_gain}"))
                self.info._can_gain = True
                log.logd(_(f"Can camera set gain : {self.info._can_gain}"))
            except NotImplementedException:
                self.info._max_gain = 0
                self.info._min_gain = 0
                self.info._can_gain = False
                log.logd(_(f"Can camera set gain : {self.info._can_gain}"))
            
            self.info._can_guiding = self.device.CanPulseGuide
            log.logd(_(f"Can camera guiding : {self.info._can_guiding}"))
            self.info._can_has_shutter = self.device.HasShutter
            log.logd(_(f"Can camera has shutter : {self.info._can_has_shutter}"))
            self.info._can_iso = False
            log.logd(_(f"Can camera set iso : {self.info._can_iso}"))
            try:
                self.info._offset = self.device.Offset
                log.logd(_(f"Camera current offset : {self.info._offset}"))
                self.info._max_offset = self.device.OffsetMax
                log.logd(_(f"Camera max offset : {self.info._max_offset}"))
                self.info._min_offset = self.device.OffsetMin
                log.logd(_(f"Camera min offset : {self.info._min_offset}"))
                self.info._can_offset = True
                log.logd(_(f"Can camera set offset : {self.info._can_offset}"))
            except InvalidOperationException:
                self.info._max_offset = 0
                self.info._min_offset = 0
                self.info._can_offset = False
                log.logd(_(f"Can camera set offset : {self.info._can_offset}"))

            self.info._is_cooling = self.device.CoolerOn
            log.logd(_(f"Is camera cooling : {self.info._is_cooling}"))
            self.info._is_exposure = CameraState.get(self.device.CameraState)
            log.logd(_(f"Is camera exposure : {self.info._is_exposure}"))
            try:
                self.info._is_guiding = self.device.IsPulseGuiding
                log.logd(_(f"Is camera guiding : {self.info._is_guiding}"))
            except NotImplementedException:
                self.info._is_guiding = False
            self.info._is_imageready = self.device.ImageReady
            log.logd(_(f"Is camera image ready : {self.info._is_imageready}"))
            self.info._is_video = False
            log.logd(_(f"Is camera video : {self.info._is_video}"))

            self.info._max_exposure = self.device.ExposureMax
            log.logd(_(f"Camera max exposure : {self.info._max_exposure}"))
            self.info._min_exposure = self.device.ExposureMin
            log.logd(_(f"Camera min exposure : {self.info._min_exposure}"))
            self.info._min_exposure_increment = self.device.ExposureResolution
            log.logd(_(f"Camera min exposure increment : {self.info._min_exposure_increment}"))
            self.info._max_binning = [self.device.MaxBinX,self.device.MaxBinY]
            log.logd(_(f"Camera max binning : {self.info._max_binning}"))

            self.info._height = self.device.CameraYSize
            log.logd(_(f"Camera frame height : {self.info._height}"))
            self.info._width = self.device.CameraXSize
            log.logd(_(f"Camera frame width : {self.info._width}"))
            self.info._max_height = self.info._height
            self.info._max_width = self.info._width
            self.info._min_height = self.info._height
            self.info._min_width = self.info._width
            self.info._depth = self.device.ImageArrayInfo
            try:
                self.info._bayer_offset_x = self.device.BayerOffsetX
                log.logd(_(f"Camera bayer offset x : {self.info._bayer_offset_x}"))
                self.info._bayer_offset_y = self.device.BayerOffsetY
                log.logd(_(f"Camera bayer offset y : {self.info._bayer_offset_y}"))
                self.info._bayer_pattern = 0
                self.info._is_color = True
            except NotImplementedException:
                self.info._bayer_offset_x = 0
                self.info._bayer_offset_y = 0
                self.info._bayer_pattern = ""
                self.info._is_color = False
            self.info._pixel_height = self.device.PixelSizeY
            log.logd(_(f"Camera pixel height : {self.info._pixel_height}"))
            self.info._pixel_width = self.device.PixelSizeX
            log.logd(_(f"Camera pixel width : {self.info._pixel_width}"))
            self.info._max_adu = self.device.MaxADU
            log.logd(_(f"Camera max ADU : {self.info._max_adu}"))
            self.info._start_x = self.device.StartX
            log.logd(_(f"Camera start x : {self.info._start_x}"))
            self.info._start_y = self.device.StartY
            log.logd(_(f"Camera start y : {self.info._start_y}"))
            self.info._subframe_x = self.device.NumX
            log.logd(_(f"Camera subframe x : {self.info._subframe_x}"))
            self.info._subframe_y = self.device.NumY
            log.logd(_(f"Camera subframe y : {self.info._subframe_y}"))
            self.info._sensor_name = self.device.SensorName
            log.logd(_(f"Camera sensor name : {self.info._sensor_name}"))
            self.info._sensor_type = Sensor.get(self.device.SensorType)
            log.logd(_(f"Camera sensor type : {self.info._sensor_type}"))

        except NotConnectedException as e:
            log.loge(_(error.NotConnected))
            return log.return_error(_(error.NotConnected,{}))
        except DriverException as e:
            pass
        except ConnectionError as e:
            log.loge(_(f"{error.NetworkError} , error : {e}"))
            return log.return_error(error.NetworkError,{"error":e})
        log.log(success.GetConfigrationSuccess)
        return log.return_success(success.GetConfigrationSuccess,{"info" : self.info.get_dict()})

    def set_configration(self, params: dict) -> dict:
        return super().set_configration(params)

    def load_configration(self) -> dict:
        return super().load_configration()

    def save_configration(self) -> dict:
        """
            Save configration of camera
            Args : None
            Return : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """
        _p = path.join
        _path = _p(getcwd() , "config","camera",self.info._name+".json")
        if not path.exists("config"):
            mkdir("config")
        if not path.exists(_p("config","camera")):
            mkdir(_p("config","camera"))
        self.info._configration = _path
        try:
            with open(_path,mode="w+",encoding="utf-8") as file:
                try:
                    file.write(dumps(self.info.get_dict(),indent=4,ensure_ascii=False))
                except JSONDecodeError as e:
                    log.loge(_(f"JSON decoder error , error : {e}"))
        except OSError as e:
            log.loge(_(f"Failed to write configuration to file , error : {e}"))
        log.log(success.SaveConfigrationSuccess)
        return log.return_success(success.SaveConfigrationSuccess,{})

    def start_exposure(self, params : dict) -> dict:
        """
            Start exposure function | 开始曝光
            Args : {
                "params" : {
                    "exposure" : float # exposure time
                    "gain" : int # gain
                    "offset" : int # offset
                    "binning" : int # binning
                    "image" : {
                        "is_save" : bool
                        "is_dark" : bool
                        "name" : str
                        "type" : str # fits or tiff of jpg
                    }
                    "filterwheel" : {
                        "enable" : boolean # enable or disable
                        "filter" : int # id of filter
                    }
                }
            }
            Returns : {
                "status" : int ,
                "message" : str,
                "params" : None
            }
            NOTE : This function is a blocking function
        """
        if self.device is None or not self.info._is_connected:
            log.logw(_(f"{error.NotConnected} , please do not execute {_getframe().f_code.co_name} command"))
            return log.return_warning(_(error.NotConnected),{})
        exposure = params.get("exposure")
        gain = params.get("gain")
        offset = params.get("offset")
        binning = params.get("binning")

        is_save = params.get("image").get("is_save")
        is_dark = params.get("image").get("is_dark")
        name = params.get("image").get("name")
        _type = params.get("image").get("type")
        # TODO : there should be well considered
        if params.get("filterwheel") is not None:
            filterwheel = params.get("filterwheel").get("enable")
            _filter = params.get("filterwheel").get("filter")
            if filterwheel:
                log.logd(_("Change"))
            if _filter:
                log.logd(_(_filter))

        if exposure is None or not self.info._min_exposure < exposure < self.info._max_exposure:
            log.loge(error.InvalidExposureValue)
            return log.return_error(error.InvalidExposureValue,{"error":exposure})
        log.logd(_(f"Exposure time : {exposure}"))
        
        try:
            # Set gain if available
            if self.info._can_gain:
                if gain is None or not self.info._min_gain < gain < self.info._max_gain:
                    gain = 20
                    log.logw(error.InvalidGainValue)
                self.device.Gain = gain
                log.logd(_(f"Set gain successfully , set to {gain}"))
            # Set offset if available
            if self.info._can_offset:
                if offset is None or offset < 0:
                    offset = 20
                    log.logw(error.InvalidOffsetValue)
                self.device.Offset = offset
                log.logd(_(f"Set offset successfully, set to {offset}"))
            # Set binning mode if available
            if self.info._can_binning:
                if binning is None or not 0 < binning < self.info._max_binning[0]:
                    binning = 1
                    log.logw(error.InvalidBinningValue)
                self.device.BinX = binning
                self.device.BinY = binning
                log.logd(_(f"Set binning successfully, set to {binning}"))

        except InvalidValueException as e:
            log.loge(_(f"Invalid value , error: {e}"))
            return log.return_error(_("Invalid value"),{"error":e})
        except NotConnectedException as e:
            log.loge(_(f"Remote device is not connected ,error: {e}"))
            return log.return_error(_(error.NotConnected),{"error":e})
        except DriverException as e:
            log.loge(_(f"Remote driver error , {e}"))
            return log.return_error(error.DriverError,{"error":e})
        except ConnectionError as e:
            log.loge(_(f"{error.NetworkError} , error : {e}"))
            return log.return_error(error.NetworkError,{"error":e})
        
        if is_dark:
            log.logd(_("Prepare to create a dark image"))

        log.log(_("Start exposure ..."))
        try:
            self.device.StartExposure(exposure,is_dark)
            self.info._is_exposure = True
            sleep(0.1)
            if not self.device.ImageReady and self.device.CameraState == CameraStates.cameraExposing:
                log.log(_("Start exposure successfully"))
                self.info._last_exposure = exposure
            else:
                log.log(_("Start exposure failed"))
            used_time = 0
            while not self.device.ImageReady:
                sleep(0.1)
                used_time += 0.1
                log.logd(_(f"Had already used time : {used_time} seconds , progress completed : {self.device.PercentCompleted}"))

                if self.device.CameraState == CameraStates.cameraError:
                    log.loge(_("Some error occurred when camera was exposuring"))
                    return log.return_error(_("Some error occurred when camera was exposuring"),{"error" : ""})
            log.log(_("Finish exposure successfully & download image ..."))
            
        except InvalidValueException as e:
            log.loge(_(f"Invalid value, error: {e}"))
            return log.return_error(_("Invalid value"),{"error":e})
        except InvalidOperationException as e:
            log.loge(_(f"Invalid operation, error: {e}"))
            return log.return_error(_("Invalid operation"),{"error":e})
        except NotConnectedException as e:
            log.loge(_(f"Remote device is not connected,error: {e}"))
            return log.return_error(_(error.NotConnected),{"error":e})
        except DriverException as e:
            log.loge(_(f"Remote driver error, {e}"))
            return log.return_error(error.DriverError,{"error":e})
        except ConnectionError as e:
            log.loge(_(f"{error.NetworkError} , error : {e}"))
            return log.return_error(error.NetworkError,{"error":e})
        finally:
            self.info._is_exposure = False
        
        if is_save is None:
            is_save = True

        if name is None:
            if self.info._image_name_format is None:
                name = "Image_" + datetime.now().strftime("%Y-%m-%d-%H:%M:%S") + "_."
            else:
                name = self.info._image_name_format
        
        if _type is None:
            if self.info._image_type is None:
                _type = "fits"
            else:
                _type = self.info._image_type

    def abort_exposure(self) -> dict:
        """
            Abort exposure operation | 停止曝光
            Args: None
            Returns:{
                "status" : int,
                "message" : str
                "params" : None
            }
            NOTE : This function must be called if exposure is still in progress when shutdown server
        """
        if not self.info._is_connected:
            log.logw(_(f"Could not abort exposure, camera is not connected"))
            return log.return_error(_(error.NotConnected),{})
        if not self.info._is_exposure:
            log.logw(_("Exposure not started , please do not execute abort_exposure() command"))
            return log.return_warning(_("Exposure not started"),{})
        try:
            self.device.StopExposure()
            sleep(0.5)
            if self.device.CameraState == CameraStates.cameraIdle:
                log.log(success.AbortExposureSuccess)
                return log.return_success(success.AbortExposureSuccess,{})
            else:
                log.log(error.AbortExposureError)
                return log.return_error(error.AbortExposureError,{"error": error.AbortExposureError})
        except NotImplementedException as e:
            log.loge(_(f"Sorry,exposure is not supported to stop , error: {e}"))
            return log.return_error(_("Sorry,exposure is not supported to stop"),{"error":e})
        except NotConnectedException as e:
            log.loge(_(f"Remote device is not connected,error: {e}"))
            return log.return_error(_(error.NotConnected),{"error":e})
        except InvalidOperationException as e:
            log.loge(_(f"Invalid operation, error: {e}"))
            return log.return_error(error.InvalidOperation,{"error":e})
        except DriverException as e:
            log.loge(_(f"Remote driver error, {e}"))
            return log.return_error(error.DriverError,{"error":e})
        except ConnectionError as e:
            log.loge(_(f"Network error while get camera configuration , error : {e}"))
            return log.return_error(_("Network error while get camera configuration"),{"error":e})
        finally:
            self.info._is_exposure = False
        
    def get_exposure_status(self) -> dict:
        """
            Get exposure status | 获取曝光状态
            Args: None
            Returns:{
                "status" : int,
                "message" : str
                "params" : {
                    "status" : int
                }
            }
        """
        if not self.info._is_connected:
            log.logw(_(f"Cannot get exposure status, camera is not connected"))
            return log.return_error(error.NotConnected,{"error": error.NotConnected})
        if not self.info._is_exposure:
            log.logw(_(f"Exposure not started, please do not execute get_exposure_status() command"))
            return log.return_warning(_("Exposure not started"),{})

        try:
            status = CameraState.get(self.device.CameraState)
        except NotConnectedException as e:
            log.loge(_(f"Remote device is not connected,error: {e}"))
            return log.return_error(_(error.NotConnected),{"error":e})
        except DriverException as e:
            log.loge(_(f"Remote driver error, {e}"))
            return log.return_error(error.DriverError,{"error":e})
        except ConnectionError as e:
            log.loge(_(f"Network error while get camera configuration, error : {e}"))
            return log.return_error(error.NetworkError,{"error":e})

        log.logd(_(f"Get camera exposure status : {status}"))
        return log.return_success(_("Get camera exposure status successfully"),{"status":status})

    def get_exposure_result(self) -> dict:
        """
            Get exposure result when exposure successful | 曝光成功后获取图像
            Args: None
            Returns:{
                "status" : int,
                "message" : str
                "params" : {
                    "image" : Base64 encoded image
                    "histogram" : List
                    "info" : Image Info
                }
            }
            NOTE : Format!
        """
        if not self.info._is_connected:
            log.logw(_(f"Cannot get exposure result, camera is not connected"))
            return log.return_error(error.NotConnected,{"error": error.NotConnected})
        if self.info._is_exposure:
            log.loge(_("Exposure is still in progress, could not get exposure result"))
            return log.return_error(_("Exposure is still in progress"),{"error": "Exposure is still in progress"})
        try:
            hist = None
            base64_encode_img = None
            info = None

            imgdata = self.device.ImageArray
            if self.info._depth is None:
                img_format = self.device.ImageArrayInfo
                if img_format.ImageElementType == ImageArrayElementTypes.Int32:
                    if self.info._max_adu <= 65535:
                        self.info._depth = 16
                    else:
                        self.info._depth = 32
                elif img_format.ImageElementType == ImageArrayElementTypes.Double:
                    self.info._depth = 64
                if img_format.Rank == 2:
                    self.info._imgarray = True
                else:
                    self.info._imgarray = False
                log.logd(_(f"Camera Image Array : {self.info._imgarray}"))
            img = None
            if self.info._depth == 16:
                img = np.uint16
            elif self.info._depth == 32:
                img = np.int32
            else:
                img = np.float64
            
            if self.info._imgarray:
                nda = np.array(imgdata, dtype=img).transpose()
            else:
                nda = np.array(imgdata, dtype=img).transpose(2,1,0)
            # Create a histogram of the image
            if self.info._depth == 16:
                hist , bins= np.histogram(nda,bins=[i for i in range(1,256)])
            elif self.info._depth == 32:
                hist, bins= np.histogram(nda,bins=[i for i in range(1,65536)])
            # Create a base64 encoded image
            bytesio = BytesIO()
            np.savetxt(bytesio, nda)
            base64_encode_img = b64encode(bytesio.getvalue())
            # Create a image information dict
            info = {
                "exposure" : self.info._last_exposure
            }
            if self.info._can_save:
                log.logd(_("Start saving image data in fits"))
                hdr = fits.Header()
                hdr['COMMENT'] = """FITS (Flexible Image Transport System) format defined in Astronomy and'
                                    Astrophysics Supplement Series v44/p363, v44/p371, v73/p359, v73/p365.
                                    Contact the NASA Science Office of Standards and Technology for the
                                    FITS Definition document""" #100 and other FITS information.'
                if self.info._depth == 16:
                    hdr['BZERO'] = 32768.0
                    hdr['BSCALE'] = 1.0
                hdr['EXPOSURE'] = self.info._last_exposure
                hdr['TIME'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                hdr['BINX'] = self.info._binning[0]
                hdr['BINY'] = self.info._binning[1]
                hdr['INSTRUME'] = self.info._sensor_type

                if self.info._can_gain:
                    hdr['GAIN'] = self.info._gain
                if self.info._can_offset:
                    hdr['OFFSET'] = self.info._offset
                if self.info._can_iso:
                    hdr['ISO'] = self.info._iso

                hdr["SOFTWARE"] = "LightAPT ASCOM Client"

                hdu = fits.PrimaryHDU(nda, header=hdr)

                _path = "Image_" + "001" + ".fits"
                try:
                    hdu.writeto(_path, overwrite=True)
                except OSError as e:
                    log.loge(_(f"Error writing image , error : {e}"))
                log.logd(_("Save image successfully"))
        except InvalidOperationException as e:
            log.loge(_(f"No image data available , error : {e}"))
            return log.return_error(_("No image data available"),{"error":e})
        except NotConnectedException as e:
            log.loge(_(f"Remote device is not connected, error : {e}"))
            return log.return_error(_(error.NotConnected),{"error":e})
        except DriverException as e:
            log.loge(_(f"Remote driver error, {e}"))
            return log.return_error(error.DriverError,{"error":e})
        except ConnectionError as e:
            log.loge(_(f"Network error while get camera configuration, error : {e}"))
            return log.return_error(error.NetworkError,{"error":e})
        
        return log.return_success(_("Save image successfully"),{"image" : base64_encode_img,"histogram" : hist,"info" : info})
        
    def start_sequence_exposure(self, params: dict) -> dict:
        """
            Start sequence exposure | 启动计划拍摄
            Args:
                params: {
                    "sequence_count": int # number of sequences
                    "sequence" : [
                        {
                            "name" : str # name of the sequence
                            "mode" : "light","dark","flat","offset",
                            "exposure" : float # exposure time in seconds
                            "gain" : int # gain
                            "offset" : int # offset
                            "iso" : int # ISO
                            "binning" : int # binning
                            "duration" : float # duration between two images
                            "repeat" : int
                            "cooling" : {
                                "enable" : bool # turn on or off cooling
                                "temperature" : float # temperature
                            },
                            "filterwheel" : {
                                "enable" : bool # turn on or off filterwheel
                                "id" : int # id of the filter
                            },
                            "image" : {
                                "is_save" : bool
                            },
                            "guiding" : {
                                "dither" : bool
                            }
                        }
                    ]
                }
        """
        if not self.info._is_connected:
            log.logw(_(f"Cannot start sequence exposure, camera is not connected"))
            return log.return_error(error.NotConnected,{"error": error.NotConnected})
        if self.info._is_exposure:
            log.logw(_(f"Sequence exposure is already in progress"))
            return log.return_error(_("Sequence exposure is already in progress"),{"error": "Sequence exposure is already in progress"})
        
        sequence_count = params.get("sequence_count")
        sequence = params.get("sequence")
        if sequence_count is None or sequence_count <= 0:
            log.logw(_(f"sequence_count must be greater than 0"))
            return log.return_error(_("Please provide a reasonable sequence count"),{"error":"sequence_count must be greater than 0"})
        if sequence is None or len(sequence) == 0:
            log.logw(_(f"sequence must not be empty"))
            return log.return_error(_("Please provide a reasonable sequence"),{"error":"sequence must not be empty"})
        
        try:
            # execute each sequence
            for _sequence in sequence:
                # check parameters provided
                name = _sequence.get("name")
                if name is None:
                    name = "Sequence"
                mode = _sequence.get("mode")
                if mode is None:
                    mode = "light"
                exposure = _sequence.get("exposure")
                if exposure is None:
                    log.loge(error.NoExposureValue)
                    return log.return_error(error.NoExposureValue,{"error":error.NoExposureValue})
                gain = _sequence.get("gain")
                if gain is None and self.info._can_gain:
                    log.loge(error.NoGainValue)
                    return log.return_error(error.NoGainValue,{"error":error.NoGainValue})
                offset = _sequence.get("offset")
                if offset is None and self.info._can_offset:
                    log.loge(error.NoOffsetValue)
                    return log.return_error(error.NoOffsetValue,{"error":error.NoOffsetValue})
                iso = _sequence.get("iso")
                if iso is None and self.info._can_iso:
                    log.loge(error.NoISOValue)
                    return log.return_error(error.NoISOValue,{"error":error.NoISOValue})
                duration = _sequence.get("duration")
                binning = _sequence.get("binning")
                if duration is None:
                    duration = 1
                repeat = _sequence.get("repeat")
                if repeat is None:
                    repeat = 1
                cooling = _sequence.get("cooling")
                filterwheel = _sequence.get("filterwheel")
                if filterwheel:
                    log.logd(_("Filter"))
                if cooling:
                    log.logd(_("Cooling"))
                log.log(_(f"Start sequence '{name}' exposure"))
                count = 1
                for _id in range(repeat):
                    log.log(_(f"Start capture no.{count} image"))
                    r = {
                        "exposure" : exposure,
                        "gain" : gain,
                        "offset" : offset,
                        "iso" : iso,
                        "binning" : binning,
                        "image" : {
                            "is_save" : True,
                            "is_dark" : False if mode != "dark" else True,
                            "name" : name + "_" + str(count) + "_",
                            "type" : "fits"
                        }
                    }
                    log.log(_(f"Start No.{_id} image capture"))
                    res = self.start_exposure(r)
                    if res.get("status") == 1:
                        log.loge(_(f"Some error occurred when camera was exposuring , error : {res.get('message')}"))
                    elif res.get("status") == 2:
                        log.logw(_(f"Some warning occurred when camera was exposuring , warning : {res.get('message')}"))
                    res = self.get_exposure_result()
                    if res.get("status") == 1:
                        log.loge(_(f"Some error occurred when getting exposure result, error : {res.get('message')}"))
                    elif res.get("status") == 2:
                        log.logw(_(f"Some warning occurred when getting exposure result, warning : {res.get('message')}"))

                    count += 1
        except DriverException as e:
            log.loge(_("Some error occurred while sequence exposure , error : {e}"))
            return log.return_error(_("Some error occurred while sequence exposure"),{"error" :e})

    def abort_sequence_exposure(self) -> dict:
        """
            Abort sequence exposure | 中止计划拍摄
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
            NOTE : After executing this function , the whole sequence will be reset
        """
        if not self.info._is_connected:
            log.loge(_("Camera is not connected , please do not execute abort sequence exposure command"))
            return log.return_error(error.NotConnected,{"error": error.NotConnected})
        try:
            res = self.abort_exposure()
            if res.get("status") == 1:
                log.loge(_(f"Some error occurred when aborting exposure, error : {res.get('message')}"))
                return log.return_error(_("Some error occurred when aborting exposure"),{"error" :res.get('message')})
            elif res.get("status") == 2:
                log.logw(_(f"Some warning occurred when aborting exposure, warning : {res.get('message')}"))
                return log.return_error(_("Some warning occurred when aborting exposure"),{"warning" :res.get('message')})
        except DriverException as e:
            log.loge(_("Some error occurred while aborting exposure, error : {e}"))
            return log.return_error(_("Some error occurred while aborting exposure"),{"error" :e})

    def pause_sequence_exposure(self) -> dict:
        """
            Pause sequence exposure | 中止计划拍摄
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    def continue_sequence_exposure(self) -> dict:
        """
            Continue sequence exposure | 继续计划拍摄
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    def get_sequence_exposure_status(self) -> dict:
        """
            Get sequence exposure status | 获取计划拍摄状态
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : int,
                }
            }
        """

    def get_sequence_exposure_result(self) -> dict:
        """
            Get sequence exposure result | 获取计划拍摄结果
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "result" : dict
                }
            }
        """