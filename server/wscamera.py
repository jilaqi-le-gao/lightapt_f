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

import base64
import json
from driver.basiccamera import CameraInfo
from server.wsdevice import wsdevice,basic_ws_info
from utils.utility import switch, ThreadPool
from utils.lightlog import lightlog
log = lightlog(__name__)

from secrets import randbelow
import gettext
_ = gettext.gettext

__version__ = '1.0.0'

__success__ = 0
__error__ = 1
__warning__ = 2

class wscamera_info(basic_ws_info,CameraInfo):
    """
        Websocket camera information container
        Public basic_ws_info and CameraInfo
    """

    _type : str
    _name : str
    _latest_json_message : str

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

    # #################################################################
    # Public from wsdevice
    # #################################################################

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

    def on_connect(self, client, server):
        return super().on_connect(client, server)

    def on_disconnect(self, client, server):
        return super().on_disconnect(client, server)
    
    def on_message(self, client, server, message):
        return super().on_message(client, server, message)

    def on_send(self, message: dict) -> bool:
        return super().on_send(message)

    def parser_json(self, message) -> None:
        """
            Override parent function | 解析JSON信息
            Args:
                message : json message
                {
                    "event" : str,
                    "uuid" : str,
                    "params" : dict
                }
            Returns:
                None
            NOTE: This is main manager of server
        """
        _message : dict
        try:
            self.info._latest_json_message = json.loads(message)
            _message = self.info._latest_json_message
        except json.JSONDecodeError:
            log.loge(_("Failed to parse JSON message"))
            return
        event = _message.get('event')
        if event is None:
            log.loge(_(f"No event found from message , {message}"))
        # There may need a thread pool to execute some functions which will cause a little time
        for case in switch(event):
            if case("RemoteStartServer"):
                self.remote_start_server(_message.get("params"))
                break
            if case("RemoteShutdownServer"):
                self.remote_shutdown_server()
                break
            if case("RemoteDashboardSetup"):
                self.remote_dashboard_setup()
                break
            if case("RemoteConnect"):
                self.remote_connect(_message.get("params"))
                break
            if case("RemoteDisconnect"):
                self.remote_disconnect()
                break
            if case("RemoteReconnect"):
                self.remote_reconnect()
                break
            if case("RemoteScanning"):
                self.remote_scanning()
                break
            if case("RemotePolling"):
                self.remote_polling()
                break
            if case("RemoteStartExposure"):
                self.remote_start_exposure(_message.get("params"))
                break
            if case("RemoteAbortExposure"):
                self.remote_abort_exposure()
                break
            if case("RemoteGetExposureStatus"):
                self.remote_get_exposure_status()
                break
            if case("RemoteGetExposureResult"):
                self.remote_get_exposure_result()
                break
            if case("RemoteCooling"):
                self.remote_cooling(_message.get("params"))
                break
            if case("RemoteGetCoolingStatus"):
                self.remote_get_cooling_status()
                break
            if case("RemoteSetCoolingTemperature"):
                self.remote_set_cooling_temperature(_message.get("params"))
                break
            if case("RemoteGetConfiguration"):
                self.remote_get_configuration()
                break
            if case("RemoteSetConfiguration"):
                self.remote_set_configuration(_message.get("params"))
                break
            log.loge(_("Unknown event received from remote client"))
            break
        

    # #################################################################
    #
    # Following methods have no return value and just send results to client
    #
    # #################################################################

    def remote_start_server(self, params: dict) -> None:
        """
            Remote start server | 远程启动服务器
            Args:
                params : dict
            Returns:
                None
            NOTE: This can only start other servers not self restart
        """

    def remote_shutdown_server(self) -> None:
        """
            Remote shutdown server | 远程关闭服务器
            Args:
                None
            Returns:
                None
            NOTE : After shutdown server , you will lose connection with client , and can only be restart!
        """

    def remote_dashboard_setup(self) -> None:
        """
            Remote dashboard setup function | 建立连接并且初始化客户端
            Args : None
            Returns : None
            ServerResult : {
                "event" : "RemoteDashboardSetup",
                "id" : int # just a random number,
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "version" : __version__
                }
            }
            NOTE : This function should be called when connection is established
        """
        r = {
            "event" : "RemoteDashboardSetup",
            "id" : randbelow(1000),
            "status" : __success__,
            "message" : "Established connection successfully",
            "params" : {
                "version" : __version__
            }
        }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_dashboard_setup() function"))

    def remote_connect(self,params : dict) -> None:
        """
            Remote connect function | 连接相机
            Args : {
                "name" : str # name of the camera,
                "type" : str # type of the camera,
                "params" : {
                    "host" : str,
                    "port" : int,
                }
            }
            Returns : None
            ServerResult : {
                "event" : "RemoteConnect",
                "id" : int # just a random number,
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "info" : CameraInfo object
                }
            }
        """
        res = self.connect(params)
        if res.get('status') != __success__:
            r = {
                "event" : "RemoteConnect",
                "id" : randbelow(1000),
                "status" : res.get('status'),
                "message" : res.get('message'),
                "params" : {
                    "reason" : self.info._latest_error
                }
            }
        else:
            r = {
                "event" : "RemoteConnect",
                "id" : randbelow(1000),
                "status" : __success__,
                "message" : res.get("message"),
                "params" : res.get('params')
            }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_connect() function"))

    def remote_disconnect(self) -> None:
        """
            Remote disconnect function | 关闭相机
            Args : None
            Returns : None
            ServerResult : {
                "event" : "RemoteDisconnect",
                "id" : int # just a random number,
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : None
            }
        """
        res = self.disconnect()
        if res.get('status')!= __success__:
            r = {
                "event" : "RemoteDisconnect",
                "id" : randbelow(1000),
                "status" : res.get('status'),
                "message" : res.get('message'),
                "params" : None
            }
        else:
            r = {
                "event" : "RemoteDisconnect",
                "id" : randbelow(1000),
                "status" : __success__,
                "message" : res.get('message'),
                "params" : None
            }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_disconnect() function"))

    def remote_reconnect(self) -> None:
        """
            Remote reconnect function | 重连相机
            Args : None
            Returns : None
            ServerResult : {
                "event" : "RemoteReconnect",
                "id" : int # just a random number,
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : None
            }
            NOTE : This function will automatically be called when camera is disconnected suddenly
        """
        res = self.reconnect()
        if res.get('status')!= __success__:
            r = {
                "event" : "RemoteReconnect",
                "id" : randbelow(1000),
                "status" : res.get('status'),
                "message" : res.get('message'),
                "params" : None
            }
        else:
            r = {
                "event" : "RemoteReconnect",
                "id" : randbelow(1000),
                "status" : __success__,
                "message" : res.get('message'),
                "params" : None
            }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_reconnect() function"))

    def remote_scanning(self) -> None:
        """
            Remote scanning function | 扫描相机
            Args : None
            Returns : None
            ServerResult : {
                "event" : "RemoteScanning",
                "id" : int # just a random number,
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "camera" : list # list of found cameras
                }
            }
        """
        res = self.scanning()
        if res.get('status')!= __success__:
            r = {
                "event" : "RemoteScanning",
                "id" : randbelow(1000),
                "status" : res.get('status'),
                "message" : res.get('message'),
                "params" : None
            }
        else:
            r = {
                "event" : "RemoteScanning",
                "id" : randbelow(1000),
                "status" : __success__,
                "message" : res.get('message'),
                "params" : {
                    "camera" : res.get('params').get('camera')
                }
            }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_scanning() function"))

    def remote_polling(self) -> None:
        """
            Remote polling function | 刷新相机信息
            Args : None
            Returns : None
            ServerResult : {
                "event" : "RemotePolling",
                "id" : int # just a random number,
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "info" : CameraInfo object
                }
            }
        """
        res = self.polling()
        if res.get('status')!= __success__:
            r = {
                "event" : "RemotePolling",
                "id" : randbelow(1000),
                "status" : res.get('status'),
                "message" : res.get('message'),
                "params" : None
            }
        else:
            r = {
                "event" : "RemotePolling",
                "id" : randbelow(1000),
                "status" : __success__,
                "message" : res.get('message'),
                "params" : {
                    "info" : res.get('params').get('info')
                }
            }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_polling() function"))

    def remote_start_exposure(self,params : dict) -> None:
        """
            Remote start exposure function | 开始曝光
            Args : {
                "params" : {
                    "exposure" : float # exposure time
                    "gain" : int # gain
                    "offset" : int # offset
                    "binning" : int # binning
                    "image" : {
                        "is_save" : bool
                        "name" : str
                        "type" : str # fits or tiff of jpg
                    }
                    "filterwheel" : {
                        "enable" : boolean # enable or disable
                        "filter" : int # id of filter
                    }
                }
            }
            Returns : None
            ServerResult : {
                "event" : "RemoteStartExposure",
                "id" : int # just a random number,
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : None
                }
            NOTE : This function is a non-blocking function,will return exposure results
        """
        res = self.start_exposure(params)
        if res.get('status')!= __success__:
            r = {
                "event" : "RemoteStartExposure",
                "id" : randbelow(1000),
                "status" : res.get('status'),
                "message" : res.get('message'),
                "params" : None
            }
        else:
            r = {
                "event" : "RemoteStartExposure",
                "id" : randbelow(1000),
                "status" : __success__,
                "message" : res.get('message'),
                "params" : None
            }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_start_exposure() function"))

    def remote_abort_exposure(self) -> None:
        """
            Remote abort exposure function | 停止曝光
            Args : None
            Returns : None
            ServerResult : {
                "event" : "RemoteAbortExposure",
                "id" : int # just a random number,
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "result" : str
                }
            }
            NOTE : This is a blocking function
        """
        res = self.abort_exposure()
        if res.get('status')!= __success__:
            r = {
                "event" : "RemoteAbortExposure",
                "id" : randbelow(1000),
                "status" : res.get('status'),
                "message" : res.get('message'),
                "params" : None
            }
        else:
            r = {
                "event" : "RemoteAbortExposure",
                "id" : randbelow(1000),
                "status" : __success__,
                "message" : res.get('message'),
                "params" : {
                    "result" : res.get('params').get('result')
                }
            }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_abort_exposure() function"))

    def remote_get_exposure_status(self) -> None:
        """
            Remote get exposure status function | 获取相机曝光状态
            Args : None
            Returns : None
            ServerResult : {
                "event" : "RemoteGetExposureStatus",
                "id" : int # just a random number,
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "status" : Camera Exposure Status Object
                }
            }
        """
        res = self.get_exposure_status()
        if res.get('status')!= __success__:
            r = {
                "event" : "RemoteGetExposureStatus",
                "id" : randbelow(1000),
                "status" : res.get('status'),
                "message" : res.get('message'),
                "params" : None
            }
        else:
            r = {
                "event" : "RemoteGetExposureStatus",
                "id" : randbelow(1000),
                "status" : __success__,
                "message" : res.get('message'),
                "params" : {
                    "status" : res.get('params').get('status')
                }
            }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_get_exposure_status() function"))

    def remote_get_exposure_result(self) -> None:
        """
            Remote get exposure result | 获取相机曝光结果
            Args : None
            Returns : None
            ServerResult : {
                "event" : "RemoteGetExposureResult",
                "id" : int # just a random number,
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "image" : Base64 encoded image,
                    "histogram" : list,
                    "info" : Image Info object
                }
            }
            NOTE : This function will be executing when the exposure is finished , don't need to call
        """
        res = self.get_exposure_result()
        if res.get('status')!= __success__:
            r = {
                "event" : "RemoteGetExposureResult",
                "id" : randbelow(1000),
                "status" : res.get('status'),
                "message" : res.get('message'),
                "params" : None
            }
        else:
            r = {
                "event" : "RemoteGetExposureResult",
                "id" : randbelow(1000),
                "status" : __success__,
                "message" : res.get('message'),
                "params" : {
                    "image" : res.get('params').get('image'),
                    "histogram" : res.get('params').get('histogram'),
                    "info" : res.get('params').get('info')
                }
            }
        

    def remote_cooling(self , params : dict) -> None:
        """
            Remote cooling function | 相机制冷
            Args : {
                "params" : {
                    "cooling" : boolean,
                    "temperature" : float,
                    "power" : float, # need camera support
                }
            }
            Returns : None
            ServerResult : {
                "event" : "RemoteCooling",
                "id" : int # just a random number,
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "result" : str
                }
            }
            NOTE : This function needs camera support , if camera is not a cooling camera , something terrible will happen 
        """

    def remote_get_cooling_status(self) -> None:
        """
            Remote get cooling status function | 获取相机制冷状态
            Args : None
            Returns : None
            ServerResult : {
                "event" : "RemoteGetCoolingStatus",
                "id" : int # just a random number,
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "status" : Camera Cooling Status Object
                }
            }
            NOTE : This function needs camera support, if camera is not a cooling camera, something ter
        """

    def remote_set_cooling_temperature(self,params : dict) -> None:
        """
            Remote set cooling temperature function | 设置相机制冷温度
            Args : {
                "params" : {
                    "temperature" : float,
                }
            }
            Returns : None
            ServerResult : {
                "event" : "RemoteSetCoolingTemperature",
                "id" : int # just a random number,
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "result" : str
                }
            }
            NOTE : This function needs camera support
        """

    def remote_get_configuration(self) -> None:
        """
            Remote get configuration function | 获取相机参数
            Args : None
            Returns : None
            ServerResult : {
                "event" : "RemoteGetConfiguration",
                "id" : int # just a random number,
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "info" : CameraInfo object
                }
            }
            NOTE : This function is blocking function, will return result to client
        """

    def remote_set_configuration(self, params : dict) -> None:
        """
            Remote set configuration function | 设置相机参数
            Args : {
                "params" : {
                    "type" : str # type of configuration
                    "value" : float # value of configuration
                }
            }
            Returns : None
            ServerResult : {
                "event" : "RemoteSetConfiguration",
                "id" : int # just a random number,
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "result" : str
                }
            }
            NOTE : This function is blocking function , will return result to client
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
                "params" : {    # parameters , depending on camera type
                    "host" : str,
                    "port" : int,
                }
            }
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "name" : str # name of the camera
                    "type" : str # type of the camera
                    "info" : CameraInfo object # information about the camera
                }
            }
        """
        if self.info._is_connected:
            log.logw(_("Had already connected to the camera , please do not connect again"))
            return log.return_warning(_("Had already connected to the camera"),{"advice" : _("Please do not connect again")})
        if params.get("type") is None or params.get("name") is None:
            log.loge(_("Please provide a type and name for the camera"))
            return log.return_error(_("Please provide a type and name for the"),{})
        try:
            # Initialize camera object,dynamic import camera class
            # Connect to camera after initialization
            for case in switch(params.get('type').lower()):
                if case("ascom"):
                    from driver.camera.ascom import camera as ascom
                    self.device = ascom()
                    if self.device.connect({"host" : params.get('host'),"port" : params.get('port'),"device_number" : 0}) != __success__:
                        log.loge(_("Failed to connect to the camera"))
                        return log.return_error(_("Failed to connect to the camera"),{"advice" : _("Connect again")})
                    log.log(_("Connected to the camera successfully"))
                    return log.return_success(_("Connected to the camera successfully"),{"info" : self.device.update_config()})
                if case("indi"):
                    from driver.camera.indi import camera as indi
                    self.device = indi()
                if case("asi"):
                    from driver.camera.zwoasi import camera as asi
                    self.device = asi()
                if case("qhy"):
                    from driver.camera.qhyccd import camera as qhy
                    self.device = qhy()
                log.loge(_("Unknown camera type , please provide a correct camera type"))
                return log.return_error(_("Unknown camera type, please provide a correct camera type"),{})
        except Exception:
            log.loge(_("Some error occurred during connect to camera"))
            return log.return_error(_("Some error occurred during connect to camera"),{})

    def disconnect(self) -> dict:
        """
            Disconnect from the camera | 与相机断开连接
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : None
            }
        """
        if not self.info._is_connected:
            log.logw(_("The camera is not connected , please do not execute disconnect command"))
            return log.return_warning(_("The camera is not connected, please do not execute disconnect command"),{})
        if self.device.disconnect()!= __success__:
            log.loge(_("Failed to disconnect from the camera"))
            return log.return_error(_("Failed to disconnect from the camera"),{"advice" : _("Disconnect again")})
        self.info._is_connected = False
        return log.return_success(_("Disconnected from the camera successfully"))

    def reconnect(self) -> dict:
        """
            Reconnect to the camera | 重连相机
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "result" : str
                }
            }
            NOTE : This function will automatically execute when camera disconnect in suddenly
        """

    def scanning(self) -> dict:
        """
            Scanning the camera | 扫描所有相机
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "list" : Camera List
                }
            }
            NOTE : This function must be called before connection
        """

    def polling(self) -> dict:
        """
            Refresh the camera infomation | 刷新相机信息
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "info" : Camera Info object
                }
            }
        """

    def update_config(self) -> dict:
        """
            Update the configuration of the camera | 更新相机信息
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "info" : CameraInfo object
                }
            }
            NOTE : This function must be called after initialization
        """

    def start_exposure(self, params : dict) -> dict:
        """
            Start the exposure | 开始曝光
            Args :
                params : {
                    "exposure" : float # exposure time
                    "gain" : int # gain
                    "offset" : int # offset
                    "binning" : int # binning
                    "filterwheel" : {
                        "enable" : boolean # enable or disable
                        "filter" : int # id of filter
                    }
                }
            Returns :
                {
                    "status" : __success__,__error__,__warning__,
                    "message" : str,
                    "params" : {
                        "result" : str
                    }
                }
            NOTE : This function is blocking
        """

    def abort_exposure(self) -> dict:
        """
            Abort the exposure | 停止曝光
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : None
            }
            NOTE : This function is blocking
        """

    def get_exposure_status(self) -> dict:
        """
            Get the exposure status | 获取曝光状态
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "status" : Camera Exposure Status Object
                }
            }
            NOTE : This function should be called while exposuring
        """

    def get_exposure_result(self) -> dict:
        """
            Get the exposure result | 获取曝光结果
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "image" : Base64 encoded image
                    "histogram" : list
                    "info" : Image Info Object
                }
            }
            NOTE : This function must be called after exposure is finished
        """

    def cooling(self , params : dict) -> dict:
        """
            Cooling the camera | 打开拍摄
            Args :
                params : {
                    "enable" : boolean # enable or disable
                    "temperature" : float # temperature
                    "power" : float
                }
            Returns :{
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : None
            }
            NOTE : This function needs camera support
        """

    def get_cooling_status(self) -> dict:
        """
            Get the cooling status | 获取制冷状态
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "status" : Camera Cooling Status Object
                }
            }
            NOTE : This function is suggested to be called while cooling
        """

    def set_cooling_temperature(self , params : dict) -> dict :
        """
            Set cooling temperature | 设置相机制冷温度
            Args :
                params : {
                    "temperature" : float
                }
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : None
            }
            NOTE : This function needs camera support
        """

    def get_configration(self) -> dict:
        """
            Get the configration | 获取配置信息
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "info" : Camera Configuration Object
                }
            }
            NOTE : This function is suggested to be called before setting configuration
        """

    def set_configration(self, params : dict) -> dict :
        """
            Set configration | 设置配置信息
            Args :
                params : {
                    "type" : str # type of configuration
                    "value" : str # value of configuration
                }
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : None
            }
            NOTE : After executing this function , we suggest to call get_configration()
        """
    
    # #############################################################
    #
    # Following functions should not be called directly by clients
    #
    # #############################################################

    # ----------------------------------------------------------------
    # Exposure functions
    # ----------------------------------------------------------------
    
    @property
    def _gain(self) -> dict:
        """
            Get the gain | 获取相机增益
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "gain" : float,
                    "max_gain" : float,
                    "min_gain" : float
                }
            }
            Call Functions:
                __max_gain()
                __min_gain()
        """

    @property.setter
    def _gain(self , gain : float) -> dict:
        """
            Set the gain | 设置相机增益
            Args :
                gain : float
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : None
            }
        """

    @property
    def _offset(self) -> dict:
        """
            Get the offset | 获取相机偏置
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "offset" : float,
                    "max_offset" : float,
                    "min_offset" : float
                }
            }
            Call Functions:
                __max_offset()
                __min_offset()
        """

    @property.setter
    def _offset(self, offset : float) -> dict:
        """
            Set the offset | 设置相机偏置
            Args :
                offset : float
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : None
            }
        """

    @property
    def _binning(self) -> dict:
        """
            Get the binning | 获取相机像素合并
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "binning" : int
                }
            }
        """

    @property.setter
    def _binning(self, binning : int) -> dict:
        """
            Set the binning | 设置相机像素合并数
            Args :
                binning : int
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : None
            }
        """

    @property
    def _exposure(self) -> dict:
        """
            Get exposure time | 获取曝光时间
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "exposure" : float
                }
            }
        """
    
    @property.setter
    def _exposure(self, exposure : float) -> dict:
        """
            Set the exposure | 设置曝光时间
            Args :
                exposure : float
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : None
            }
        """

    @property
    def _temperature(self) -> dict:
        """
            Get the temperature | 获取温度
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "temperature" : float
                }
            }
            NOTE : This function needs camera support
        """

    @property.setter
    def _temperature(self, temperature : float) -> dict:
        """
            Set the temperature | 设置相机温度
            Args :
                temperature : float
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : None
            }
            NOTE : This function needs camera support
        """

    # ----------------------------------------------------------------
    # Camera Properties
    # ----------------------------------------------------------------
    
    @property
    def _frame(self) -> dict:
        """
            Get the frame of camera | 获取相机画幅
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "height" : int # height of sensor
                    "width" : int # width of sensor
                    "pixel_height" : int # pixel height of sensor
                    "pixel_width" : int # pixel width of sensor
                    "start_x" : int # start x
                    "start_y" : int # start y
                    "subframe_x" : int # subframe x position
                    "subframe_y" : int # subframe y position
                    "sensor_name" : str 
                    "sensor_type" : str
                }
            }
            Call Functions:
                __frame_height()
                __frame_width()
                __frame_pixel_height()
                __frame_pixel_width()
                __frame_start_x()
                __frame_start_y()
                __frame_subframe_x()
                __frame_subframe_y()
                __frame_sensor_name()
                __frame_sensor_type()
        """

    @property
    def __frame_height(self) -> dict:
        """
            Get the frame height of camera | 获取相机画幅高
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "height" : int # height of sensor
                }
            }
        """

    @property
    def __frame_width(self) -> dict:
        """
            Get the frame width of camera | 获取相机画幅宽
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "width" : int # width of sensor
                }
            }
        """

    @property
    def __frame_pixel_height(self) -> dict:
        """
            Get the frame pixel height of camera | 获取相机像素高度
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "pixel_height" : int # pixel height of sensor
                }
            }
        """

    @property
    def __frame_pixel_width(self) -> dict:
        """
            Get the frame pixel width of camera | 获取相机像素宽度
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "pixel_width" : int # pixel width of sensor
                }
            }
        """

    @property
    def __frame_start_x(self) -> dict:
        """
            Get the frame start x position of camera | 获取相机起始位置
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "start_x" : int # start x
                }
            }
        """

    @property
    def __frame_start_y(self) -> dict:
        """
            Get the frame start y position of camera | 获取相机起始位置
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "start_y" : int # start y
                }
            }
        """

    @property
    def __frame_subframe_x(self) -> dict:
        """
            Get the frame subframe x position of camera | 获取相机子画幅起始位置
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "subframe_x" : int # subframe x position
                }
            }
        """

    @property
    def __frame_subframe_y(self) -> dict:
        """
            Get the frame subframe y position of camera | 获取相机子画幅起始位置
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "subframe_y" : int # subframe y position
                }
            }
        """

    @property
    def __frame_sensor_type(self) -> dict:
        """
            Get the frame sensor type of camera | 获取相机芯片类型
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "sensor_type" : int # sensor type
                }
            }
            NOTE : This function needs software support
        """

    @property
    def __frame_sensor_name(self) -> dict:
        """
            Get the frame sensor name of camera | 获取相机芯片名称
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "sensor_name" : str # sensor name
                }
            }
        """

    # ----------------------------------------------------------------
    # Exposure Setting Limitations
    # ----------------------------------------------------------------

    @property
    def __max_gain(self) -> dict:
        """
            Get the max gain setting of camera | 获取最大相机增益
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "max_gain" : int # max gain setting
                }
            }
        """

    @property
    def __min_gain(self) -> dict:
        """
            Get the min gain setting of camera | 获取最小相机增益
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "min_gain" : int # min gain setting
                }
            }
        """

    @property
    def __max_offset(self) -> dict:
        """
            Get the max offset setting of camera | 获取最大相机偏置
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "max_offset" : int # max offset setting
                }
            }
        """

    @property
    def __min_offset(self) -> dict:
        """
            Get the minimum offset of camera | 获取最小相机偏置
            Args : None
            Returns : {
                "status" : __success__,__error__,__warning__,
                "message" : str,
                "params" : {
                    "min_offset" : int # min offset setting
                }
            }
        """