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
from libs.websocket.websocket_server import WebsocketServer
from utils.webutils import check_port
from utils.lightlog import lightlog
log = lightlog(__name__)

import json
import gettext
_ = gettext.gettext

class basic_ws_info(object):
    """
        Basic information containers,read with calling get_dict() and will recieve a dictionary
    """

    host : str
    port : int
    debug : bool
    threaded : bool
    running = False
    connected = False
    ssl : dict
    
    def get_dict(self) -> dict:
        """Return dictionary"""

class wsdevice(object):
    """
        Basic websocket device interface based on libs.websocket.
        Every device will open a standard websocket server and should be connected alone.
        THis may use many system source , but we can still have a try.
    """

    def __init__(self) -> None:
        """Constructor"""
        self.info = basic_ws_info()
        self.ws = None
        self.device = None

    def __del__(self) -> None:
        """Destructor"""

    def on_connect(self, client, server):
        """
            Connection Event | 连接事件\n
            Args:
                client: ws
                server: ws
            Returns: None
            NOTE: This function can be overriden by subclasses
        """

    def on_disconnect(self, client, server):
        """
            Disconnect Event | 断开连接事件\n
            Args:
                client: ws
                server: ws
            Returns: None
            NOTE: This function can be overriden by subclasses
        """

    def on_message(self, client, server, message):
        """
            Message Event | 消息事件\n
            Args:
                client: ws
                server: ws
                message: str
            Returns: None
            NOTE: This function can not be overriden by subclasses.And must call parser_json()
        """
        self.parser_json(str(message))

    def parser_json(self, message):
        """
            Parser JSON Message | 解析JSON字符串\n
            This function likes a manager of all other functions.
            If a message is received from the client, it will choose what function to execute.
            Args:
                message: str
            Returns: None
            NOTE: This function must be overriden by subclasses.And do not use 'match'!
        """

    def on_send(self, message : dict) -> bool:
        """
            Send message to client | 将信息发送至客户端
            Args:
                message: dict
            Returns: True if message was sent successfully
        """
        if not isinstance(message, dict):
            log.loge(_("Unknown format of message"))
            return False
        try:
            self.ws.send_message_to_all(json.dumps(message))
        except json.JSONDecodeError as exception:
            log.loge(_(f"Failed to parse message into JSON format , error {exception}"))
            return False
        return True 

    def start_server(self, host : str, port : int, debug = False, ssl = {}) -> dict:
        """
            Start websocket server | 启动Websocket服务器\n
            Create a new server and automatically choose the right port.\n
            Args:
                host: str # default is '127.0.0.1'
                port: int # default is 5000
                debug: bool # default is False
                ssl: {
                    "enable": False,
                    "cert": str # file path
                }
            Returns: dict
                {
                    "status": int,
                    "message": str,
                    "params": {
                        "host": host,
                        "port": port
                        "debug": debug,
                    }
                }
            NOTE: This function do not have any format to send to client while being called
        """
        if not isinstance(host,str) or not isinstance(port,int) or not isinstance(debug,bool):
            log.loge(_("Invalid type of parameters given"))
            return log.return_error(_("Invalid type of parameters given"),{})
        if not 0 < port < 65535:
            log.loge(_("Websocket server port must between 0 and 65535"))
            return log.return_error(_("Websocket server port must between 0 and 65535"),{})
        while check_port(host,port):
            log.logw(_("Websocket server port had been used,try to choose a different port"))
            port += 1
        if ssl is not None:
            log.logw(_("SSL Mode is still not supported"))
        try:
            self.ws = WebsocketServer(host=host, port=port)
            self.ws.set_fn_new_client(self.on_connect)
            self.ws.set_fn_client_left(self.on_disconnect)
            self.ws.set_fn_message_received(self.on_message)
            self.ws.run_forever(threaded=True)
            self.info.host = host
            self.info.port = port
            self.info.debug = debug
            self.info.ssl = ssl
            self.info.running = True
        except Exception:
            log.loge(_("Some error occurred while creating websocket server"))
            log.return_error(_("Some error occurred while creating websocket server"),{})
        log.log(_(f"Start websocket server successfully and listen on {host}:{port}"))
        return log.return_success(_("Start websocket server successfully and listen on {host}:{port}"),{})
    
    def stop_server(self) -> dict:
        """
            Stop the server | 停止服务器\n
            Kill the server and send gracefully disconnection to clients connected.\n
            Args: None
            Returns:
                {
                    "status" : int,
                    "message" : str
                    "params" : None
                }
            NOTE: This function must be called before killing main thread
        """ 
        if not self.info.running:
            log.loge_(_("Server is not running , please do not execute stop_server()"))
            return log.return_error(_("Server is not running, please do not execute stop_server()"),{})
        self.ws.shutdown_gracefully()
        log.log(_("Shutting down websocket server gracefully"))
        self.info.running = False
        return log.return_success(_("Shutting down websocket server gracefully")) 

    def restart_server(self) -> dict:
        """
            Restart server | 重启服务器\n
            Restart current server and reconnect with the device and client.\n
            Args: None
            Returns:
                {
                    "status" : int,
                    "message" : str,
                    "params" : {
                        "device" : self.device
                    }
                }
        """
        self.stop_server()
        self.start_server(self.info.host,self.info.port,self.info.debug,self.info.ssl)
        return log.return_success(_("Restart websocket server successfully"),{})

    def shutdown_server(self) -> dict:
        """
            Shutdown the websocket server | 停止服务器
            Args: None
            Returns:
                {
                    "status" : int,
                    "message" : str,
                    "params" : None
                }
            NOTE : After executing this function , the server will be shutdown
        """
        if not self.info.running:
            log.loge(_("Server is not running"))
            return log.return_error(_("Server is not running"),{})
        self.ws.shutdown()
        self.info.running = False
        log.log(_("Server is shutting down , please wait for a moment"))
        return log.return_success(_("Websocket server shutdown successfully"),{})

    def remote_dashboard_setup(self) -> None:
        """
            Setup the connection with client | 建立与客户端的连接\n
            Args: None
            Returns: None
            NOTE: This function will be called when the connection is established
        """
    
    def remote_stop_server(self) -> None:
        """
            Stop the connection with client | 建立与客户端的连接\n
            Args: None
            Returns: None
        """

    def remote_restart_server(self) -> None:
        """
            Remote restart server | 重启服务器\n
            Restart current server and reconnect with the device and client.\n
            Args: None
            Returns: None
        """

    def remote_shutdown_server(self) -> None:
        """
            Remote shutdown server | 停止服务器\n
            Restart current server and reconnect with the device and client.\n
            Args: None
            Returns: None
        """

    def generate_message(self, event : str,status : int,message : str,params : dict) -> dict:
        """
            Generate message to client | 生成消息
            Args:
                event : str
                status : int
                message : str
                params : dict
            Returns:
                {
                    "event" : str
                    "status" : int,
                    "message" : str,
                    "params" : dict
                }
        """
        r = {
            "event" : event,
            "status" : status,
            "id" : randbelow(10000),
            "message" : message,
            "params" : params
        }
        return r