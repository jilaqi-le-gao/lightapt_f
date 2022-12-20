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


from secrets import randbelow
from server.basic.wsdevice import wsdevice,basic_ws_info
from server.basic.focuser import BasicFocuserAPI,BasicFocuserInfo
import gettext
import json
from driver.focuser.ascom import focuser as ascom
from libs.websocket import websocket_server
from utils.utility import switch , ThreadPool
from utils.lightlog import lightlog
log = lightlog(__name__)

_ = gettext.gettext

__version__ = '1.0.0'

class wsfocuser_info(basic_ws_info,BasicFocuserInfo):
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

class wsfocuser(wsdevice,BasicFocuserAPI):
    """
        Websocket Focuser Object
    """

    def __init__(self,_type : str, name : str, host : str, port : int, debug : bool, threaded : bool, ssl : dict) -> None:
        """
            Initializer function | 初始化\n
            Args:
                type : str # Type of Focuser
                name : str # Name of Focuser
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
        self.info = wsfocuser_info()

        self.info.host = host if host is not None else "127.0.0.1"
        self.info.port = port if port is not None else 5000
        self.info.debug = debug if debug is not None else False
        self.info.threaded = threaded if threaded is not None else True

        if self.start_server(self.info.host,self.info.port,False,True).get('status') != 0:
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
            if case("RemoteMoveStep"):
                self.remote_move_step(_message.get("params"))
                break
            if case("RemoteMoveTo"):
                self.remote_move_to(_message.get("params"))
                break
            if case("RemoteGetTemperature"):
                self.remote_get_temperature()
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
            Remote connect function | 连接电调
            Args : {
                "name" : str # name of the Focuser,
                "type" : str # type of the Focuser,
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
                    "info" : FocuserInfo object
                }
            }
        """
        res = self.connect(params)
        r = {
            "event" : "RemoteConnect",
            "id" : randbelow(1000),
            "status" : res.get("status"),
            "message" : res.get("message"),
            "params" : res.get('params')
        }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_connect() function"))

    def remote_disconnect(self) -> None:
        """
            Remote disconnect function | 关闭电调
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
            "status" : res.get("status"),
            "message" : res.get("message"),
            "params" : res.get("params")
         }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_disconnect() function"))

    def remote_reconnect(self) -> None:
        """
            Remote reconnect function | 重连电调
            Args : None
            Returns : None
            ServerResult : {
                "event" : "RemoteReconnect",
                "id" : int # just a random number,
                "status" : int,
                "message" : str,
                "params" : None
            }
            NOTE : This function will automatically be called when Focuser is disconnected suddenly
        """
        res = self.reconnect()
        r = {
            "event" : "RemoteReconnect",
            "id" : randbelow(1000),
            "status" : res.get("status"),
            "message" : res.get('message'),
            "params" : res.get('params'),
        }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_reconnect() function"))

    def remote_scanning(self) -> None:
        """
            Remote scanning function | 扫描电调
            Args : None
            Returns : None
            ServerResult : {
                "event" : "RemoteScanning",
                "id" : int # just a random number,
                "status" : int,
                "message" : str,
                "params" : {
                    "Focuser" : list # list of found Focusers
                }
            }
        """
        res = self.scanning()
        r = {
            "event" : "RemoteScanning",
            "id" : randbelow(1000),
            "status" : res.get("status"),
            "message" : res.get('message'),
            "params" : {
                "focuser" : res.get("params").get("list")
            }
        }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_scanning() function"))

    def remote_polling(self) -> None:
        """
            Remote polling function | 刷新电调信息
            Args : None
            Returns : None
            ServerResult : {
                "event" : "RemotePolling",
                "id" : int # just a random number,
                "status" : int,
                "message" : str,
                "params" : {
                    "info" : FocuserInfo object
                }
            }
        """
        res = self.polling()
        r = {
            "event" : "RemotePolling",
            "id" : randbelow(1000),
            "status" : res.get("status"),
            "message" : res.get('message'),
            "params" : {
                "info" : res.get('params').get('info')
            }
        }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_polling() function"))

    def remote_move_step(self, params : dict) -> None:
        """
            Remote move function | 电调步进(区分正负)
            Args :
                params : {
                    "step": int # Distinguish between positive and negative
                }
            Returns : None
            ServerResult : {
                "event" : "RemoteMoveStep",
                "id" : int # just a random number,
                "status" : int,
                "message" : str,
                "params" : {
                    "target" : int 
                }
            }
            NOTE : We suggest to execute get_movement_status() after executing this function
        """
        res = self.move_step(params)
        r = {
            "event" : "RemoteMoveStep",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : res.get('message'),
            "params" : {
                "target" : res.get('params').get('target')
            }
        }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_move_step() function"))

    def remote_move_to(self ,params : dict) -> None:
        """
            Remote move to target position function | 电调步进到指定位置
            Args :
                params : {
                    "target": int # target position
                }
            Returns : None
            ServerResult : {
                "event" : "RemoteMoveTo",
                "id" : int # just a random number,
                "status" : int,
                "message" : str,
                "params" : {
                    "target" : int 
                }
            }
            NOTE : We suggest to execute get_movement_status() after executing this function
        """
        res = self.move_to(params)
        r = {
            "event" : "RemoteMoveTo",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : res.get('message'),
            "params" : {
                "target" : res.get('params').get('target')
            }
        }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_move_to() function"))

    def remote_get_movement_status(self) -> None:
        """
            Get the status of movement | 获取电调状态
            Args : None
            Returns : None
            ServerResult : {
                "event" : "RemoteGetMovementStatus",
                "id" : int # just a random number,
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : Focuser Movement Status
                }
            }
        """
        res = self.get_movement_status()
        r = {
            "event" : "RemoteGetMovementStatus",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : res.get('message'),
            "params" : {
                "status" : res.get("params").get('status'),
            }
        }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_get_movement_status() function"))

    def remote_get_temperature(self) -> None:
        """
            Get the focuser temperature | 获取电调温度
            Args : None
            Returns : None
            ServerResult : {
                "event" : "RemoteGetFocuserTemperature",
                "id" : int # just a random number,
                "status" : int,
                "message" : str,
                "params" : {
                    "temperature" : float
                }
            }
            NOTE : This function needs focuser support
        """
        res = self.get_temperature()
        r = {
            "event" : "RemoteGetFocuserTemperature",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : res.get('message'),
            "params" : {
                "temperature" : res.get('params').get('temperature')
            }
        }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_get_temperature() function"))

    def remote_get_configuration(self) -> None:
        """
            Get the configuration | 获取电调配置
            Args : None
            Returns : None
            ServerResult : {
                "event" : "RemoteGetConfiguration",
                "id" : int # just a random number,
                "status" : int,
                "message" : str,
                "params" : {
                    "info" : FocuserInfo object
                }
            }
            NOTE : This function wiil be automatically called after executing remote_set_configuration()
        """
        res = self.get_configuration()
        r = {
            "event" : "RemoteGetConfiguration",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : res.get('message'),
            "params" : {
                "info" : res.get('params').get('info')
            }
        }
        if self.on_send(r) is not True:
            log.loge_(_("Failed to send message while executing remote_get_configuration() function"))

    def remote_set_configuration(self, params : dict) -> None:
        """
            Set the configuration | 设置电调配置
            Args :
                params : {
                    "type" : str # type of the configuration
                    "value" : int # value of the configuration
                }
            Returns : None
            ServerResult : {
                "event" : "RemoteSetConfiguration",
                "id" : int # just a random number,
                "status" : int,
                "message" : str,
                "params" : {
                    "type" : str,
                    "value" : int
                }
            }
            NOTE : We suggest after executing this function , you should call get_configration()
        """
        res = self.set_configuration(params)
        r = {
            "event" : "RemoteSetConfiguration",
            "id" : randbelow(1000),
            "status" : res.get('status'),
            "message" : res.get('message'),
            "params" : {
                "type" : res.get('params').get('type'),
                "value" : res.get('params').get('value')
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
            Connect to the focuser | 连接电调
            Args : {
                "name" : str # name of the focuser
                "type" : str # type of the focuser
                "params" : {    # parameters , depending on focuser type
                    "host" : str,
                    "port" : int,
                }
            }
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "name" : str # name of the focuser
                    "type" : str # type of the focuser
                    "info" : FocuserInfo object # information about the focuser
                }
            }
        """

    def disconnect(self) -> dict:
        """
            Disconnect from the focuser | 断开连接
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    def reconnect(self) -> dict:
        """
            Reconnect to the focuser | 重连电调
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "result" : str
                }
            }
            NOTE : This function will automatically execute when focuser disconnect in suddenly
        """

    def scanning(self) -> dict:
        """
            Scanning the focuser | 扫描所有电调
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "list" : focuser List
                }
            }
            NOTE : This function must be called before connection
        """

    def polling(self) -> dict:
        """
            Polling the focuser newest infomation | 获取电调最新信息
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "info" : BasicFocuserInfo object
                }
            }
        """

    def move_step(self, params : dict) -> dict:
        """
            Focuser move given step | 电调移动指定步数
            Args :
                params : {
                    "step" : int
                }
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    def move_to(self , params : dict) -> dict:
        """
            Move to target position | 移动至指定位置
            Args :
                params : {
                    "position" : int
                }
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    def get_temperature(self) -> dict:
        """
            Get focuser temperature | 获取电调温度
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "temperature" : float
                }
            }
            NOTE : This function needs focuser support
        """

    def get_configration(self) -> dict:
        """
            Get the configration | 获取配置信息
            Args : None
            Returns : {
                "status" : int,
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
                "status" : int,
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

    @property
    def _step(self) -> dict:
        """
            Get current step
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "step" : int
                }
            }
        """
    
    @property.setter
    def _step(self, params : dict) -> dict:
        """
            Set the step to be executed | 设置电调位置
            Args :
                params : {
                    "step" : int
                }
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    @property
    def _temperature(self) -> dict:
        """
            Get current temperature | 获取电调当前温度
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "temperature" : float
                }
            }
            NOTE : This function needs focuser support
        """