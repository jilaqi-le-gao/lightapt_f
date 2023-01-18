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
# System Library
from json import JSONDecodeError,dumps, loads
import os
from secrets import randbelow
import threading
from time import sleep
import asyncio
# Third party libraries
from libs.websocket.websocket_server import WebsocketServer
# Built-in libraries
from server.wscamera import WsCameraInterface
from server.wstelescope import WsTelescopeInterface
from utils.utility import switch
from utils.i18n import _
from utils.lightlog import lightlog
logger = lightlog(__name__)

import server.config as c

class wsinfo(object):
    """
        Websocket information container
    """

    is_running = False

    host : str
    port : int
    ssl : bool
    key : str
    cert : str

    client_id = 1 # id of clients connected
    max_clients = 10 # max number of clients , default is 10

class ws_server(object):
    """
        Wescoket server class.
        Architecture:
                                             |-- wscamera -- camera -- pyindi/alpyca -- indi/ascom -- camera
                                             |
                                             |-- wstelescope -- telescope -- pyindi/alpyca -- indi/ascom -- telescope
                                             |
            WebUI -- websocket -- wsserver --|-- wsfocuser -- focuser -- pyindi/alpyca -- indi/ascom -- focuser
                                             |
                                             |-- wsguider -- guider -- socket -- PHD2
                                             |
                                             |-- wssolver -- command line --|-- astrometry
                                                                            |
                                                                            |-- astap
        This means this class is like the brain of the program.
        All of the commands from clients will be executed there and return the results to the user.
    """

    def __init__(self ) -> None:
        """
            Initialize the server.
        """
        self.info = wsinfo()
        # Initialize the devices object
        self.camera = WsCameraInterface()
        self.telescope = WsTelescopeInterface()

    def __del__(self) -> None:
        """
            Destroy the server
        """
        if self.info.is_running:
            self.stop_server()

    def start_server(self,host : str,port : int,ssl : bool,key : str,cert : str) -> None:
        """
            Start the websocket server on the specified port and host.
            If the SSL mode is enabled , will use the key and certificate provided.\n
            Args : 
                host : str # the hostname of the server , default is 0.0.0.0
                port : int # the port of the server, default is 8000
                ssl : bool # SSL mode , default is False
                key : str # the path of the key file, default is None
                cert : str # the path of the certificate file, default is None
        """
        _host = host if host is not None and isinstance(host, str) else "0.0.0.0"
        _port = port if port is not None and isinstance(port, int) else 8000
        _ssl = ssl if ssl is not None and isinstance(ssl, bool) else False
        _key = key if key is not None and isinstance(key, str) else None
        _cert = cert if cert is not None and isinstance(cert, str) else None
        # Check if the port is valid
        if not 0 < _port < 65536:
            logger.loge(_("The port number provided is so fucking invalid"))
            return
        # If the SSL mode is enabled
        if _ssl:
            logger.log(_("SSL mode is enabled"))
            # Check if the key file exists
            _key_path = os.path.join("config","ssl",_key)
            if not os.path.exists(_key_path):
                logger.loge(_("SSL key not found"))
            else:
                logger.log(_("SSL key is found in {}").format(_key_path))
            # Check if the certificate file exists
            _cert_path = os.path.join("config","ssl",_cert)
            if not os.path.exists(_cert_path):
                logger.loge(_("SSL certificate not found"))
            else:
                logger.log(_("SSL certificate is found in {}").format(_cert_path))
        else:
            logger.logw(_("SSL protection is not available , do not be like this if you want to present the host in public domain"))
        # Trying to create the websocket server
        try:
            c.ws = WebsocketServer(host = _host, port = _port,key = _key,cert = _cert)
            # Set connect event
            c.ws.set_fn_new_client(self.on_connect)
            # Set disconnect event
            c.ws.set_fn_client_left(self.on_disconnect)
            # Set message event
            c.ws.set_fn_message_received(self.on_message)
            # Start the server
            c.ws.run_forever(threaded=True)
            # Load the infomation into a global variable
            self.info.host = _host
            self.info.port = _port
            self.info.ssl = _ssl
            self.info.key = _key if _ssl else ""
            self.info.cert = _cert if _ssl else ""

            self.info.is_running = True
            logger.log(_("Setting up websocket server successfully on {}:{}").format(_host,_port))
        except Exception as e:
            logger.loge(_("Some error occurred during setting up the websocket server : {}").format(str(e)))

    def stop_server(self) -> None:
        """
            Stop the current server and means the star journey is stopped.
            Args : None
            Returns : None
        """
        if not self.info.is_running:
            logger.log(_("Server is not running"))
            return
        
        try:
            c.ws.shutdown_gracefully(status=114115,reason=b'shutdown by user')
            logger.log(_("Server shutdown successful , goodbye!"))
        except Exception as e:
            logger.loge(_("Failed to shutdown the websocket server : {}").format(str(e)))

    def restart_server(self) -> None:
        """
            Restart the current server.
            Args : None
            Returns : None
        """
        if not self.info.is_running:
            logger.log(_("Server is not running"))
            return
        # Trying to restart the server
        try:
            self.stop_server()
            # Just reduce the cost of the cpu and memory usage
            sleep(1)
            self.start_server(host=self.info.host, port=self.info.port,ssl = self.info.ssl,key = self.info.key,cert=self.info.cert)
            logger.log(_("Restart websocket server successfully"))
        except Exception as e:
            logger.loge(_("Failed to restart the websocket server : {}").format(str(e)))

    def on_connect(self, client, server) -> None:
        """
            Connection Event | 连接事件\n
            Args:
                client: ws
                server: ws
            Returns: None
        """
        if self.info.client_id > self.info.max_clients:
            c.ws.deny_new_connections(status=403,reason=b'Too many clients')
        logger.log(_("Established connection with new client , id is {}").format(self.info.client_id))
        self.info.client_id += 1

    def on_disconnect(self, client, server) -> None:
        """
            Disconnect Event | 断开连接事件\n
            Args:
                client: ws
                server: ws
            Returns: None
            NOTE: This function can be overriden by subclasses
        """
        logger.log(_("Disconnecting from the client"))
        self.info.client_id -= 1

    def on_message(self, client, server, message) -> None:
        """
            Message Event | 消息事件\n
            Args:
                client: ws
                server: ws
                message: str
            Returns: None
            NOTE: This function can not be overriden by subclasses.And must call parser_json()
        """
        asyncio.run(self.parser_json(str(message)))
        #self.parser_json(str(message))

    def on_send(self, message : dict) -> bool:
        """
            Send message to client | 将信息发送至客户端
            Args:
                message: dict
            Returns: True if message was sent successfully
            Message Example:
                status : int ,
                message : str,
                params : dict
        """
        if not isinstance(message, dict) or message.get("status") is None or message.get("message") is None:
            logger.loge(_("Unknown format of message"))
            return False
        try:
            c.ws.send_message_to_all(dumps(message))
        except JSONDecodeError as exception:
            logger.loge(_(f"Failed to parse message into JSON format , error {exception}"))
            return False
        return True 

    def generate_message(self, event : str,status : int,message : str,params : dict) -> dict:
        """
            Generate message to client | 生成消息
            Args:
                event : str
                status : int
                message : str
                params : dict
            Returns:
                    "event" : str
                    "status" : int,
                    "message" : str,
                    "params" : dict
        """
        return {
            "event" : event,
            "status" : status,
            "id" : randbelow(10000),
            "message" : message,
            "params" : params
        }

    async def parser_json(self, message : str) -> None:
        """
            Parser JSON Message | 解析JSON字符串\n
            This function likes a manager of all other functions.
            If a message is received from the client, it will choose what function to execute.
            Args:
                message: str
            Returns: None
        """
        _message : dict
        try:
            _message = loads(message)
        except JSONDecodeError as e:
            logger.loge(_("Failed to parse JSON message : {}").format(str(e)))
            self.on_send({"status" : 1 , "message" : _("Failed to parse JSON message")})
            return
        event = _message.get('event')
        event_type = _message.get('type')
        if event is None or event_type is None:
            logger.loge(_("No event found in message , {}").format(message.replace("\n","")))
            self.on_send({"status" : 1 , "message" : _("No event found in message")})
            return
        for case in switch(event_type):
            # Camera event
            if case("camera"):
                for _case in switch(event):
                    if _case("RemoteConnect"):
                        self.camera.remote_connect(_message.get("params"))
                        break
                    if _case("RemoteDisconnect"):
                        self.camera.remote_disconnect()
                        break
                    if _case("RemoteReconnect"):
                        self.camera.remote_reconnect()
                        break
                    if _case("RemoteScanning"):
                        self.camera.remote_scanning()
                        break
                    if _case("RemotePolling"):
                        self.camera.remote_polling()
                        break
                    if _case("RemoteStartExposure"):
                        self.camera.remote_start_exposure(_message.get("params"))
                        break
                    if _case("RemoteAbortExposure"):
                        self.camera.remote_abort_exposure()
                        break
                    if _case("RemoteGetExposureStatus"):
                        self.camera.remote_get_exposure_status()
                        break
                    if _case("RemoteGetExposureResult"):
                        self.camera.remote_get_exposure_result()
                        break
                    if _case("RemoteStartSequenceExposure"):
                        self.camera.remote_start_sequence_exposure(_message.get("params"))
                        break
                    if _case("RemoteAbortSequenceExposure"):
                        self.camera.remote_abort_sequence_exposure()
                        break
                    if _case("RemotePauseSequenceExposure"):
                        self.camera.remote_pause_sequence_exposure()
                        break
                    if _case("RemoteContinueSequenceExposure"):
                        self.camera.remote_continue_sequence_exposure()
                        break
                    if _case("RemoteGetSequenceExposureStatus"):
                        self.camera.remote_get_sequence_exposure_status()
                        break
                    if _case("RemoteGetSequenceExposureResults"):
                        self.camera.remote_get_sequence_exposure_results()
                        break
                    if _case("RemoteCooling"):
                        self.camera.remote_cooling(_message.get("params"))
                        break
                    if _case("RemoteCoolingTo"):
                        self.camera.remote_cooling_to(_message.get("params"))
                        break
                    if _case("RemoteGetCoolingStatus"):
                        self.camera.remote_get_cooling_status()
                        break
                    if _case("RemoteGetConfiguration"):
                        self.camera.remote_get_configuration(_message.get("params"))
                        break
                    if _case("RemoteSetConfiguration"):
                        self.camera.remote_set_configuration(_message.get("params"))
                        break
                    logger.loge(_("Unknown camera event received from remote client"))
                    break
                break
            # All of the telescope events
            if case("telescope"):
                for _case in switch(event):
                    if _case("RemoteConnect"):
                        self.telescope.remote_connect(_message.get("params"))
                        break
                    if _case("RemoteDisconnect"):
                        self.telescope.remote_disconnect()
                        break
                    if _case("RemoteReconnect"):
                        self.telescope.remote_reconnect()
                        break
                    if _case("RemoteScanning"):
                        self.telescope.remote_scanning()
                        break
                    if _case("RemotePolling"):
                        self.telescope.remote_polling()
                        break
                    if _case("RemoteGoto"):
                        self.telescope.remote_goto(_message.get("params"))
                        break
                    if _case("RemoteAbortGoto"):
                        self.telescope.remote_abort_goto()
                        break
                    if _case("RemotePark"):
                        self.telescope.remote_park()
                        break
                    if _case("RemoteUnpark"):
                        self.telescope.remote_unpack()
                        break
                    if _case("RemoteHome"):
                        self.telescope.remote_home()
                        break
                    logger.loge(_("Unknown telescope event received from remote client"))
                    break
                break
            if case("server"):
                for _case in switch(event):
                    if _case("RemoteDashboardSetup"):
                        self.remote_dashboard_setup()
                    break
                break
            break
        

    # #################################################################
    # 
    # NOTE : All of the functions below should be non-blocking
    #
    # #################################################################

    # #################################################################
    # Server Events
    # #################################################################

    def remote_dashboard_setup(self) -> None:
        """
            Remote dashboard setup function | 初始化连接
            Args : None
            Returns : None
        """
        r = {
            "event" : "RemoteDashboardSetup",
            "id" : randbelow(1000),
            "status" : 0,
            "message" : "",
            "params" : None
        }
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing start_server command"))

    def remote_start_server(self , params : dict) -> None:
        """
            Remote Start Server Event | 服务器启动
            Args: 
                params : dict # host + port + ssl + key + cert
            Returns: None
            NOTE : Is this function a little bit stupid , if the server is not running , how we recieve message from client
        """
        r = {
            "event" : "RemoteStartServer",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : None
        }
        if self.info.is_running:
            logger.loge(_("Server is running"))
            r["message"] = _("Server is running")
        else:
            self.start_server(params.get("host","0.0.0.0"),
                params.get("port",8000),
                params.get("ssl",False),
                params.get("key",None),
                params.get("cert",None))
            if not self.info.is_running:
                logger.loge(_("Failed to start server"))
                r["message"] = _("Failed to start server")
            else:
                r["status"] = 0
                r["message"] = _("Server is running")
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing start_server command"))

    def remote_stop_server(self) -> None:
        """
            Remote Stop Server Event | 停止服务器
            Args: None
            Returns: None
        """
        r = {
            "event" : "RemoteStopServer",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : None
        }
        if not self.info.is_running:
            logger.loge(_("Server is not running"))
            r["message"] = _("Server is not running")
        else:
            self.stop_server()
            if self.info.is_running:
                logger.loge(_("Failed to stop server"))
                r["message"] = _("Failed to stop server")
            else:
                r["status"] = 0
                r["message"] = _("Server is stopped")
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing stop_server command"))

    def remote_restart_server(self) -> None:
        """
            Remote Restart Server Event | 重启服务器
            Args: None
            Returns: None
        """
        r = {
            "event" : "RemoteRestartServer",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : None
        }
        if not self.info.is_running:
            logger.loge(_("Server is not running"))
            r["message"] = _("Server is not running")
        else:
            self.restart_server()
            if not self.info.is_running:
                logger.loge(_("Failed to restart server"))
                r["message"] = _("Failed to restart server")
            else:
                r["status"] = 0
                r["message"] = _("Server is restarted")
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing restart_server command"))

    def remote_change_configuration(self , params : dict) -> None:
        """
            Remote Change Configuration Event | 更新服务器配置
            Args: 
                params : dict
            Returns: None
        """
        r = {
            "event" : "RemoteChangeConfiguration",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : params
        }
        if not self.info.is_running:
            logger.loge(_("Server is not running"))
            r["message"] = _("Server is not running")
        else:
            self.change_configuration(params)
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing remote_change_configuration command"))

    def change_configuration(self,params : dict) -> bool:
        """
            Change Configuration Event | 更新服务器配置
            Args: 
                params : dict
            Returns: bool
        """
        
    def remote_save_configuration(self) -> None:
        """
            Remote Save Configuration Event | 保存服务器配置
            Args: None
            Returns: None
        """
        r = {
            "event" : "RemoteSaveConfiguration",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : None
        }
        if not self.info.is_running:
            logger.loge(_("Server is not running"))
            r["message"] = _("Server is not running")
        else:
            if not self.save_configuration():
                logger.loge(_("Failed to save configuration"))
                r["message"] = _("Failed to save configuration")
            else:
                r["status"] = 0
                r["message"] = _("Configuration saved")
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing save_configuration command"))

    def save_configuration(self) -> bool:
        """
            Save Configuration Event | 保存服务器配置
            Args: None
            Returns: bool
        """
