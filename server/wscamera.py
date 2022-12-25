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
from server.basic.wsdevice import wsdevice,basic_ws_info
from server.wsexception import WSCameraError as error
from server.wsexception import WSCameraWarning as warning
from server.wsexception import WSCameraSuccess as success

from utils.utility import switch
from utils.lightlog import lightlog
log = lightlog(__name__)

from secrets import randbelow
import gettext
_ = gettext.gettext
import json

__version__ = '1.0.0'

class wscamera_info(basic_ws_info,BasicCameraInfo):
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
                "connected" : self._is_connected,
                "exposure" : self._is_exposure,
                "video" : self._is_video,
                "guiding" : self._is_guiding,
                "cooling" : self._is_cooling,
                "fastreadout" : self._is_fastreadout,
                "imgready" : self._is_imgready,
            }
        }
        return r

class wscamera(wsdevice,BasicCameraAPI):
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
        res = self.start_server(self.info.host,self.info.port,False,True)
        if res.get('status') == 1:
            log.loge(_("Failed to start websocket server"))
        elif res.get("status") == 2:
            log.logw(_("Start websocket server with warning"))
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
        log.logd(_("Established connection with client"))
        return super().on_connect(client, server)

    def on_disconnect(self, client, server):
        log.logd(_("Disconnected from client"))
        return super().on_disconnect(client, server)
    
    def on_message(self, client, server, message):
        msg = message.replace('\n','')
        log.logd(_(f"Received message : {msg}"))
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
            if case("RemoteStopServer"):
                self.remote_stop_server()
                break
            if case("RemoteShutdownServer"):
                self.remote_shutdown_server()
                break
            if case("RemoteRestartServer"):
                self.remote_restart_server()
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
            if case("RemoteStartSequenceExposure"):
                self.remote_start_sequence_exposure(_message.get("params"))
                break
            if case("RemoteAbortSequenceExposure"):
                self.remote_abort_sequence_exposure()
                break
            if case("RemotePauseSequenceExposure"):
                self.remote_pause_sequence_exposure()
                break
            if case("RemoteContinueSequenceExposure"):
                self.remote_continue_sequence_exposure()
                break
            if case("RemoteGetSequenceExposureStatus"):
                self.remote_get_sequence_exposure_status()
                break
            if case("RemoteGetSequenceExposureResults"):
                self.remote_get_sequence_exposure_results()
                break
            if case("RemoteCooling"):
                self.remote_cooling(_message.get("params"))
                break
            if case("RemoteCoolingTo"):
                self.remote_cooling_to(_message.get("params"))
                break
            if case("RemoteGetCoolingStatus"):
                self.remote_get_cooling_status()
                break
            if case("RemoteGetConfiguration"):
                self.remote_get_configuration(_message.get("params"))
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
        res = self.start_server(params.get("host"),params.get("port"),params.get("debug"),params.get("ssl"))
        r = {
            "event" : "RemoteStartServer",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : str(res.get('message')),
            "params" : None
        }
        if self.on_send(r) is not True:
            log.loge(_(f"Failed to send remote start server event"))
        
    def remote_stop_server(self) -> None:
        """
            Remote stop server | 停止服务器
            Args:
                None
            Returns:
                None
            NOTE: This can only stop other servers not self restart
        """
        res = self.stop_server()
        r = {
            "event" : "RemoteStopServer",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : str(res.get('message')),
            "params" : None
        }
        if self.on_send(r) is not True:
            log.loge(_(f"Failed to send remote stop server event"))

    def remote_shutdown_server(self) -> None:
        """
            Remote shutdown server | 远程关闭服务器
            Args:
                None
            Returns:
                None
            NOTE : After shutdown server , you will lose connection with client , and can only be restart!
        """
        res = self.shutdown_server()
        r = {
            "event" : "RemoteShutdownServer",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : str(res.get('message')),
            "params" : None
        }
        if self.on_send(r) is not True:
            log.loge(_(f"Failed to send remote shutdown server event"))

    def remote_dashboard_setup(self) -> None:
        """
            Remote dashboard setup function | 建立连接并且初始化客户端
            Args : None
            Returns : None
            ServerResult : {
                "event" : "RemoteDashboardSetup",
                "id" : int # just a random number,
                "status" : int,
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
            "status" : 0,
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
                "status" : int,
                "message" : str,
                "params" : {
                    "info" : BasicCameraInfo object
                }
            }
        """
        res = self.connect(params)
        r = {
            "event" : "RemoteConnect",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : str(res.get("message")),
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
                "status" : int,
                "message" : str,
                "params" : None
            }
        """
        res = self.disconnect()
        r = {
            "event" : "RemoteDisconnect",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : str(res.get('message')),
            "params" : res.get('params')
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
                "status" : int,
                "message" : str,
                "params" : None
            }
            NOTE : This function will automatically be called when camera is disconnected suddenly
        """
        res = self.reconnect()
        r = {
            "event" : "RemoteReconnect",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : str(res.get('message')),
            "params" : res.get('params')
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
                "status" : int,
                "message" : str,
                "params" : {
                    "camera" : list # list of found cameras
                }
            }
        """
        res = self.scanning()
        r = {
            "event" : "RemoteScanning",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : str(res.get('message')),
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
                "status" : int,
                "message" : str,
                "params" : {
                    "info" : CameraInfo object
                }
            }
        """
        res = self.polling()
        r = {
            "event" : "RemotePolling",
            "id" : randbelow(1000),
            "status" : res.get("status"),
            "message" : str(res.get('message')),
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
                "status" : int,
                "message" : str,
                "params" : None
                }
            NOTE : This function is a non-blocking function,will return exposure results
        """
        res = self.start_exposure(params)
        r = {
            "event" : "RemoteStartExposure",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : str(res.get('message')),
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
                "status" : int,
                "message" : str,
                "params" : {
                    "result" : str
                }
            }
            NOTE : This is a blocking function
        """
        res = self.abort_exposure()
        r = {
            "event" : "RemoteAbortExposure",
            "id" : randbelow(1000),
            "status" : res.get("status"),
            "message" : str(res.get('message')),
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
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : Camera Exposure Status Object
                }
            }
        """
        res = self.get_exposure_status()
        r = {
            "event" : "RemoteGetExposureStatus",
            "id" : randbelow(1000),
            "status" : res.get("status"),
            "message" : str(res.get('message')),
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
                "status" : int,
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
        r = {
            "event" : "RemoteGetExposureResult",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : str(res.get('message')),
            "params" : {
                "image" : res.get('params').get('image'),
                "histogram" : res.get('params').get('histogram'),
                "info" : res.get('params').get('info')
            }
        }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_get_exposure_result() function"))
    
    def remote_start_sequence_exposure(self, params : dict) -> None:
        """
            Remote start exposure function | 开始录屏
            Args :
                params : {
                    "sequence_number" : int
                    "sequence" : dict
                }
            Returns : None
            ServerResult : {
                "event" : "RemoteStartSequenceExposure",
                "id" : int,
                "status" : int,
                "message" : str,
                "params" : None
            }
        """
        res = self.start_sequence_exposure(params)
        r = {
            "event" : "RemoteStartSequenceExposure",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : str(res.get('message')),
            "params" : None
        }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_start_sequence_exposure() function"))

    def remote_abort_sequence_exposure(self) -> None:
        """
            Remote abort exposure function | 停止计划拍摄
            Args :
                None
            Returns : None
            ServerResult : {
                "event" : "RemoteAbortSequenceExposure",
                "id" : int,
                "status" : int,
                "message" : str,
                "params" : None
            }
            NOTE : After executing this command , we will totally cancel the sequence exposure
        """
        res = self.abort_sequence_exposure()
        r = {
            "event" : "RemoteAbortSequenceExposure",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : str(res.get('message')),
            "params" : None
        }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_abort_sequence_exposure() function"))

    def remote_pause_sequence_exposure(self) -> None:
        """
            Remote pause exposure function | 停止计划拍摄
            Args :
                None
            Returns : None
            ServerResult : {
                "event" : "RemotePauseSequenceExposure",
                "id" : int,
                "status" : int,
                "message" : str,
                "params" : None
            }
            NOTE : After executing this command, you can still continue sequence exposures
        """
        res = self.pause_sequence_exposure()
        r = {
            "event" : "RemotePauseSequenceExposure",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : str(res.get('message')),
            "params" : None
        }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_pause_sequence_exposure() function"))

    def remote_continue_sequence_exposure(self) -> None:
        """
            Remote continue sequence exposure | 继续计划拍摄
            Args :
                None
            Returns : None
            ServerResult : {
                "event" : "RemoteContinueSequenceExposure",
                "id" : int,
                "status" : int,
                "message" : str,
                "params" : None
            }
            NOTE : After executing this command, you will continue sequence exposures
        """
        res = self.continue_sequence_exposure()
        r = {
            "event" : "RemoteContinueSequenceExposure",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : str(res.get('message')),
            "params" : None
        }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_continue_sequence_exposure() function"))

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
                "status" : int,
                "message" : str,
                "params" : {
                    "result" : str
                }
            }
            NOTE : This function needs camera support , if camera is not a cooling camera , something terrible will happen 
        """
        res = self.cooling(params)
        r = {
            "event" : "RemoteCooling",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : str(res.get('message')),
            "params" : {
                "result" : res.get('params').get('result')
            }
        }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_cooling() function"))

    def remote_get_cooling_status(self) -> None:
        """
            Remote get cooling status function | 获取相机制冷状态
            Args : None
            Returns : None
            ServerResult : {
                "event" : "RemoteGetCoolingStatus",
                "id" : int # just a random number,
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : Camera Cooling Status Object
                }
            }
            NOTE : This function needs camera support, if camera is not a cooling camera, something ter
        """
        res = self.get_cooling_status()
        r = {
            "event" : "RemoteGetCoolingStatus",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : str(res.get('message')),
            "params" : {
                "status" : res.get('params').get('status')
            }
        }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_get_cooling_status() function"))

    def remote_get_configuration(self,params : dict) -> None:
        """
            Remote get configuration function | 获取相机参数
            Args : None
            Returns : None
            ServerResult : {
                "event" : "RemoteGetConfiguration",
                "id" : int # just a random number,
                "status" : int,
                "message" : str,
                "params" : {
                    "info" : CameraInfo object
                }
            }
            NOTE : This function is blocking function, will return result to client
        """
        res = self.get_configration(params)
        r = {
            "event" : "RemoteGetConfiguration",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : str(res.get('message')),
            "params" : {
            "info" : res.get('params').get('info')
            }
        }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_get_configuration() function"))

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
                "status" : int,
                "message" : str,
                "params" : {
                    "result" : str
                }
            }
            NOTE : This function is blocking function , will return result to client
        """
        res = self.set_configration(params)
        r = {
            "event" : "RemoteSetConfiguration",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : str(res.get('message')),
            "params" : {
                "result" : res.get('params').get('result')
            }
        }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_set_configuration() function"))

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
                "status" : int,
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
            self.remote_polling()
            return log.return_warning(_("Had already connected to the camera"),{"advice" : _("Please do not connect again")})
        if params.get("type") is None or params.get("name") is None:
            log.loge(_("Please provide a type and name for the camera"))
            return log.return_error(_("Please provide a type and name for the"),{})
        try:
            _type = params.get('type')
            # Initialize camera object,dynamic import camera class
            # Connect to camera after initialization
            for case in switch(_type):
                if case("ascom"):
                    from server.driver.camera.ascom import AscomCameraAPI as camera
                    self.device = camera()
                    res = self.device.connect({"host" : params.get('host'),"port" : params.get('port'),"device_number" : 0})
                    if res.get("status") != 0:
                        log.loge(error.ConnectError)
                        return log.return_error(error.ConnectError,{"error":str(res.get("message"))})
                    break
                if case("indi"):
                    from server.driver.camera.indi import camera as indi
                    self.device = indi()
                    res = self.device.connect({"host" : params.get('host'),"port" : params.get('port')})
                    if res.get("status") != 0:
                        log.loge(error.ConnectError)
                        return log.return_error(error.ConnectError,{"error":str(res.get("message"))})
                    break
                if case("asi"):
                    from server.driver.camera.zwoasi import camera as asi
                    self.device = asi()
                    res = self.device.connect({"name" : params.get("name")})
                    if res.get("status") != 0:
                        log.loge(error.ConnectError)
                        return log.return_error(error.ConnectError,{"error":res.get("mesaage")})
                    break
                if case("qhy"):
                    from server.driver.camera.qhyccd import camera as qhy
                    self.device = qhy()
                    res = self.device.connect({"name" : params.get("name")})
                    if res.get("status") != 0:
                        log.loge(error.ConnectError)
                        return log.return_error(error.ConnectError,{"error":res.get("error")})
                    break
                log.loge(_("Unknown camera type , please provide a correct camera type"))
                return log.return_error(_("Unknown camera type, please provide a correct camera type"),{})
        except Exception as e:
            log.loge(_(f"Some error occurred during connect to camera, error : {e}"))
            return log.return_error(_("Some error occurred during connect to camera"),{"error":e})
        log.log(_(success.ConnectSuccess))
        self.info._is_connected = True
        return log.return_success(_(success.ConnectSuccess),{"info" : self.device.info.get_dict()})

    def disconnect(self) -> dict:
        """
            Disconnect from the camera | 与相机断开连接
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """
        if not self.info._is_connected:
            log.logw(_("The camera is not connected , please do not execute disconnect command"))
            return log.return_warning(_("The camera is not connected, please do not execute disconnect command"),{})
        res = self.device.disconnect()
        if res.get("status") == 1:
            log.loge(_("Failed to disconnect from the camera"))
            return log.return_error(_("Failed to disconnect from the camera"),{"advice" : _("Disconnect again")})
        elif res.get("status") == 2:
            log.logw(_("Disconnect with the camera with warning"))
            return log.return_warning(_("Disconnect with the camera with warning"),{"warning" : res.get("params").get("warning")})
        self.info._is_connected = False
        log.log(_("Disconnect from the camera successfully"))
        return log.return_success(_("Disconnected from the camera successfully"))

    def reconnect(self) -> dict:
        """
            Reconnect to the camera | 重连相机
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "result" : str
                }
            }
            NOTE : This function will automatically execute when camera disconnect in suddenly
        """
        if not self.info._is_connected:
            log.logw(_("The camera is not connected, please do not execute reconnect command"))
            return log.return_warning(_("The camera is not connected, please do not execute reconnect command"),{})
        res = self.device.reconnect()
        if res.get("status") == 1:
            log.loge(_("Failed to reconnect to the camera"))
            return log.return_error(_("Failed to reconnect to the camera"),{"advice" : _("Reconnect again")})
        elif res.get("status") == 2:
            log.logw(_("Reconnect with the camera with warning"))
            return log.return_warning(_("Reconnect with the camera with warning"),{"warning" : res.get("params").get("warning")})
        log.log(_("Reconnect to camera successfully"))
        return log.return_success(_("Reconnect to camera successfully"),{})

    def scanning(self) -> dict:
        """
            Scanning the camera | 扫描所有相机
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "list" : Camera List
                }
            }
            NOTE : This function must be called before connection
        """
        res = self.device.scanning()
        if res.get("status") == 1:
            log.loge(_("Failed to scan the camera"))
            return log.return_error(_("Failed to scan the camera"),{"advice" : _("Scan again")})
        elif res.get("status") == 2:
            log.logw(_("Scan with the camera with warning"))
            return log.return_warning(_("Scan with the camera with warning"),{"warning" : res.get("params").get("warning")})
        log.log(_(f"Scanning the camera successfully , Found : {res.get('params').get('list')}"))
        return log.return_success(_("Scanning the camera successfully"),{"list" : res.get("params").get("list")})


    def polling(self) -> dict:
        """
            Refresh the camera infomation | 刷新相机信息
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "info" : Camera Info object
                }
            }
        """
        res = self.device.polling()
        if res.get("status") == 1:
            log.loge(_("Failed to refresh the camera infomation"))
            return log.return_error(_("Failed to refresh the camera infomation"),{"advice" : _("Refresh again")})
        elif res.get("status") == 2:
            log.logw(_("Refresh the camera infomation with warning"))
            return log.return_warning(_("Refresh the camera infomation with warning"),{"warning" : res.get("params").get("warning")})
        log.log(_("Refresh the camera infomation successfully"))
        return log.return_success(_("Refresh the camera infomation successfully"),{"info" : res.get('params').get('info')})

    def update_config(self) -> dict:
        """
            Update the configuration of the camera | 更新相机信息
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "info" : CameraInfo object
                }
            }
            NOTE : This function must be called after initialization
        """
        res = self.device.update_config()
        if res.get("status") == 1:
            log.loge(_("Failed to update the camera configuration"))
            return log.return_error(_("Failed to update the camera configuration"),{"advice" : _("Update the camera configuration again")})
        elif res.get("status") == 2:
            log.logw(_("Update the camera configuration with warning"))
            return log.return_warning(_("Update the camera configuration with warning"),{"warning" : res.get("params").get("warning")})
        log.log(_("Update camera configuration successfully"))
        return log.return_success(_("Update camera configuration successfully"),{"info" : res.get("info")})

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
                    "status" : int,
                    "message" : str,
                    "params" : {
                        "result" : str
                    }
                }
            NOTE : This function is a blocking function
        """
        if params.get("exposure") is None or not 0 < params.get('exposure') < 1000000:
            log.loge(_("Unreasonable exposure time was given , please give a possible number"))
        if params.get("gain") is None or params.get('gain') < 0:
            log.loge(_("Unreasonable gain was given, please give a possible number"))
        if params.get("offset") is None or params.get('offset') < 0:
            log.loge(_("Unreasonable offset was given, please give a possible number"))
        if params.get("binning") is None or not 1 <= params.get('bin') <= 8:
            log.loge(_("Unreasonable binning was given, please give a possible number"))
        res = self.device.start_exposure(params)
        if res.get("status") == 1:
            log.loge(_("Failed to start the exposure"))
            return log.return_error(_("Failed to start the exposure"),{"advice" : _("Start exposure again")})
        elif res.get("status") == 2:
            log.logw(_("Start exposure with warning"))
            return log.return_warning(_("Start exposure with warning"),{"warning" : res.get("params").get("warning")})
        log.log(_("Exposure started successfully"))
        return log.return_success(_("Exposure started successfully"),{"result" : res.get("params").get("result")})
        

    def abort_exposure(self) -> dict:
        """
            Abort the exposure | 停止曝光
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
            NOTE : This function is blocking
        """
        res = self.device.abort_exposure()
        if res.get("status") == 1:
            log.loge(_("Failed to abort the exposure"))
            return log.return_error(_("Failed to abort the exposure"),{"advice" : _("Abort exposure again")})
        elif res.get("status") == 2:
            log.logw(_("Abort exposure with warning"))
            return log.return_warning(_("Abort exposure with warning"),{"warning" : res.get("params").get("warning")})
        log.log(_("Exposure aborted successfully"))
        return log.return_success(_("Exposure aborted successfully"),{})

    def get_exposure_status(self) -> dict:
        """
            Get the exposure status | 获取曝光状态
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : Camera Exposure Status Object
                }
            }
            NOTE : This function should be called while exposuring
        """
        res = self.device.get_exposure_status()
        if res.get("status") == 1:
            log.loge(_("Failed to get the exposure status"))
            return log.return_error(_("Failed to get the exposure status"),{})
        elif res.get("status") == 2:
            log.logw(_("Get exposure status with warning"))
            return log.return_warning(_("Get exposure status with warning"),{"warning" : res.get("params").get("warning")})
        log.log(_("Get exposure status successfully"))
        return log.return_success(_("Get exposure status successfully"),{"params" : res.get("params").get("status")})

    def get_exposure_result(self) -> dict:
        """
            Get the exposure result | 获取曝光结果
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "image" : Base64 encoded image
                    "histogram" : list
                    "info" : Image Info Object
                }
            }
            NOTE : This function must be called after exposure is finished
        """
        res = self.device.get_exposure_result()
        if res.get("status") == 1:
            log.loge(_("Failed to get the exposure result"))
            return log.return_error(_("Failed to get the exposure result"),{})
        elif res.get("status") == 2:
            log.logw(_("Get exposure result with warning"))
            return log.return_warning(_("Get exposure result with warning"),{"warning" : res.get("params").get("warning")})
        log.log(_("Get exposure result successfully"))
        return log.return_success(_("Get exposure result successfully"),{"params" : res.get("params")})

    def start_sequence_exposure(self, params: dict) -> dict:
        """
            Start the sequence exposure | 计划拍摄
            Args : 
                params : {
                    "sequence_number" : int, # number of sequences
                    "sequence" : {
                        {
                            "name" : str # name of the sequence
                            "type" : str # type of the sequence , light dark flat
                            "exposure" : float # exposure time of each image
                            "repeat" : int # number of times to repeat
                            "start_time" : int # start time of the sequence
                            "duration" : int # duration of the sequence
                        }
                    }
                }
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
            TODO : This function should be considered carefully
        """
        if params.get("sequence_number") is None:
            return log.return_error(_("Sequence number is required"),{})
        if params.get("sequence") is None:
            return log.return_error(_("Sequence is required"),{})
        res = self.device.start_sequence_exposure(params.get("sequence_number"))
        if res.get("status") == 1:
            log.loge(_("Failed to start sequence exposure"))
            return log.return_error(_("Failed to start sequence exposure"),{})
        elif res.get("status") == 2:
            log.logw(_("Start sequence exposure with warning"))
            return log.return_warning(_("Start sequence exposure with warning"),{"warning" : res.get("params").get("warning")})
        log.log(_("Finish sequence exposure successfully"))
        return log.return_success(_("Finish sequence exposure successfully"),{"params" : res.get("params")})

    def abort_sequence_exposure(self) -> dict:
        """
            Abort the sequence exposure | 停止计划拍摄
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """
        res = self.device.abort_sequence_exposure()
        if res.get("status") == 1:
            log.loge(_("Failed to abort sequence exposure"))
            return log.return_error(_("Failed to abort sequence exposure"),{})
        elif res.get("status") == 2:
            log.logw(_("Abort sequence exposure with warning"))
            return log.return_warning(_("Abort sequence exposure with warning"),{"warning" : res.get("params").get("warning")})
        log.log(_("Abort sequence exposure successfully"))
        return log.return_success(_("Abort sequence exposure successfully"),{})

    def pause_sequence_exposure(self) -> dict:
        """
            Pause the sequence exposure | 中止计划拍摄
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
        """
        res = self.device.pause_sequence_exposure()
        if res.get("status") == 1:
            log.loge(_("Failed to pause sequence exposure"))
            return log.return_error(_("Failed to pause sequence exposure"),{})
        elif res.get("status") == 2:
            log.logw(_("Pause sequence exposure with warning"))
            return log.return_warning(_("Pause sequence exposure with warning"),{"warning" : res.get("params").get("warning")})
        log.log(_("Pause sequence exposure successfully"))
        return log.return_success(_("Pause sequence exposure successfully"),{})

    def continue_sequence_exposure(self) -> dict:
        """
            Continue the sequence exposure | 继续计划拍摄
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
        """
        res = self.device.continue_sequence_exposure()
        if res.get("status") == 1:
            log.loge(_("Failed to continue sequence exposure"))
            return log.return_error(_("Failed to continue sequence exposure"),{})
        elif res.get("status") == 2:
            log.logw(_("Continue sequence exposure with warning"))
            return log.return_warning(_("Continue sequence exposure with warning"),{"warning" : res.get("params").get("warning")})
        log.log(_("Continue sequence exposure successfully"))
        return log.return_success(_("Continue sequence exposure successfully"),{})

    def cooling(self , params : dict) -> dict:
        """
            Cooling the camera | 相机制冷
            Args :
                params : {
                    "enable" : boolean # enable or disable
                    "temperature" : float # temperature
                    "power" : float
                }
            Returns :{
                "status" : int,
                "message" : str,
                "params" : None
            }
            NOTE : This function needs camera support
        """
        if not self.info._can_set_temperature:
            log.loge(error.NotSupportTemperatureControl)
            return log.return_error(error.NotSupportTemperatureControl,{})
        if params.get('enable') is None:
            params['enable'] = False
        if params.get('temperature') is None:
            return log.return_error(_("Please provide a temperature"),{})
        if params.get('power') is None:
            return log.return_error(_("Please provide a power"),{})
        res = self.device.cooling(params)
        if res.get("status") != 0:
            log.loge(error.CoolingError)
            return log.return_error(error.CoolingError,{"error":str(res.get("message"))})
        log.log(success.CoolingSuccess)
        return log.return_success(success.CoolingSuccess,{})

    def cooling_to(self, params: dict) -> dict:
        """
            Cooling the camera | 打开拍摄
            Args :
                params : {
                    "temperature" : float # temperature
                }
            Returns:
                {
                    "status" : int,
                    "message" : str,
                    "params" : None
                }
        """
        if not self.info._can_set_temperature:
            log.loge(_("Camera does not support temperature control"))
            return log.return_error(_("Camera does not support temperature control"),{})
        if params.get('temperature') is None or not -100 < params.get('temperature') < 50:
            return log.return_error(_("Please provide a valid temperature"),{})
        res = self.device.cooling_to(params)
        if res.get("status") == 1:
            log.loge(_("Failed to set the cooling"))
            return log.return_error(_("Failed to set the cooling"),{"advice" : _("Set cooling failed")})
        elif res.get("status") == 2:
            log.logw(_("Set cooling with warning"))
            return log.return_warning(_("Set cooling with warning"),{"warning" : res.get("params").get("warning")})
        log.log(_("Set cooling successfully"))
        return log.return_success(_("Set cooling successfully"),{})

    def get_cooling_status(self) -> dict:
        """
            Get the cooling status | 获取制冷状态
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : Camera Cooling Status Object
                }
            }
            NOTE : This function is suggested to be called while cooling
        """
        res = self.device.get_cooling_status()
        if res.get("status") == 1:
            log.loge(_("Failed to get the cooling status"))
            return log.return_error(_("Failed to get the cooling status"),{})
        elif res.get("status") == 2:
            log.logw(_("Get cooling status with warning"))
            return log.return_warning(_("Get cooling status with warning"),{})
        log.log(_("Get cooling status successfully"))
        return log.return_success(_("Get cooling status successfully"),{"params" : res.get("params").get("status")})

    def get_configration(self , params : dict) -> dict:
        """
            Get the configration | 获取配置信息
            Args : 
                params:{
                    "type" : str
                }
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "info" : Camera Configuration Object
                }
            }
            NOTE : This function is suggested to be called before setting configuration
        """
        if params.get("type") is None:
            return log.return_error(_("Please provide a type"),{})
        res = self.device.get_configration(params)
        if res.get("status") == 1:
            log.loge(_("Failed to get the configration"))
            return log.return_error(_("Failed to get the configration"),{})
        elif res.get("status") == 2:
            log.logw(_("Get configration with warning"))
            return log.return_warning(_("Get configration with warning"),{})
        log.log(_("Get configration successfully"))
        return log.return_success(_("Get configration successfully"),{"params" : res.get("params").get("configration")})

    def set_configration(self, params : dict) -> dict :
        """
            Set configration | 设置配置信息
            Args :
                params : {
                    "type" : str # type of configuration
                    "value" : str # value of configuration
                }
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
            NOTE : After executing this function , we suggest to call get_configration()
        """
        if params.get('type') is None or params.get('value') is None:
            return log.return_error(_("Please provide a valid configration"),{})
        res = self.device.set_configration(params)
        if res.get("status") == 1:
            log.loge(_("Failed to set the configration"))
            return log.return_error(_("Failed to set the configration"),{})
        elif res.get("status") == 2:
            log.logw(_("Set configration with warning"))
            return log.return_warning(_("Set configration with warning"),{})
        log.log_("Set configration successfully")
        return log.return_success(_("Set configration successfully"),{})
