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

from libs.websocket.websocket_server import WebsocketServer
from driver.telescope.ascom import telescope as ascom

from utils.utility import switch,ThreadPool
from utils.lightlog import lightlog
log = lightlog(__name__)

import json
import gettext
_ = gettext.gettext

class wstelescope_info(object):
    """
        Websocket Telescope information
    """
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
            "started": self._started,
            "connected": self._connected,
            "settings": {
                "timeout": self._timeout,
                "max_thread_num": self._max_thread_num,
                "debug": self._debug
            }
        }

class wstelescope(object):
    """
        Websocket Telescope Object
        Each telescope will have a standard websocket server
        This means that we can connect to the server flexible
        However, we need to remove the websocket server on time
    """

    def __init__(self):
        self._ws = None
        self._info = wstelescope_info()
        self._device = None
        self._threadpool = ThreadPool(max_workers=3)
    
    def __del__(self) -> None:
        if self._ws:
            self._ws.close()
            self._ws = None

    def start_server(self, host : str, port : int, debug = False) -> dict:
        """
            Start the websocket server for telescope
            Args:
                host : str # host default to "127.0.0.1"
                port : int # port default to 5000
                debug : bool # debug mode 
            Returns:
                dict:
                    {
                        "status" : "success","error","warning","debug"
                        "message" : str
                        "params" : {
                            "host" : "127.0.0.1",
                            "port" : 5000
                        }
                    }
        """
        _host,_port = host,port
        if _host is None or not isinstance(_host,str):
            _host = "127.0.0.1"
        if _port is None or not isinstance(_port,port):
            _port = 5000
        try:
            self._ws = WebsocketServer(host = _host, port = _port)
            self._ws.set_fn_new_client(self.on_connect)
            self._ws.set_fn_client_left(self.on_disconnect)
            self._ws.set_fn_message_received(self.on_message)
            self._ws.run_forever(threaded=True)
        except Exception as exception:
            log.loge(_(f"Faild to start websocket server , error : {exception}"))
            return {
                "status" : "error",
                "message" : "Failed to start websocket server",
                "params" : None
            }
        log.log(_(f"Started websocket server on host : {_host} port : {_port}"))
        return {
            "status" : "success",
            "message" : "Started websocket server",
            "params" : {
                "host" : _host,
                "port" : _port
            }
        }

    def stop_server(self) -> dict:
        """
            Stop the websocket server
            Returns:
                dict:
                    {
                        "status" : "success","error","warning","debug"
                        "message" : str
                        "params" : {
                            "error" : str,
                            "debug" : str
                        }
                    }
            Note : This method must be called before stop the program
        """
        if self._ws:
            self._ws.disconnect_clients_gracefully()
            self._ws.shutdown_gracefully()
            self._ws = None
            return {
                "status" : "success",
                "message" : "Stopped websocket server",
                "params" : None
            }
        return {
            "status" : "warning",
            "message" : "No websocket server",
            "params" : None
        }

    def restart_server(self) -> dict:
        """
            Restart the websocket server
            Returns:
                dict:
                    {
                        "status" : "success","error","warning","debug"
                        "message" : str
                        "params" : {
                            "error" : str,
                            "debug" : str
                        }
                    }
        """

    def on_connect(self , client , server) -> None:
        """
            Connect Event
            Called when a client connects to the server
            Args:
                client : Client
                server : Server
            Returns:
                None
        """
        log.log(_("Established connection with client successfully"))
        self._info._connected = True

    def on_disconnect(self,client, server) -> None:
        """
            Disconnect Event
            Called when a client disconnects from the server
            Args:
                client : Client
                server : Server
            Returns:
                None
        """
        log.log(_("Disconnected websocket client successfully"))
        self._info._connected = False

    def on_message(self,client, server, message) -> None:
        """
            Message Event
            Called when a client sends a message to the server
            Args:
                client : Client
                server : Server
                message : str
            Returns:
                None
        """
        log.logd(_(f"Client({client['id']}) responded : {message}"))
        if not isinstance(message , str) : 
            log.loge(_("Unknown message format , please"))
        self.parser_json(message)

    def parser_json(self,message) -> dict:
        """
            Parser JSON message into dict format and execute functions called
            Args:
                message (str): JSON message
            Return:
                None
        """
        try:
            data = json.loads(message)
        except json.JSONDecodeError as exception:
            log.loge(_(f"Unknown format of message , error : {exception}"))
            return log.return_error("Unknown format of message",{"error" : exception})
        method = data.get("method")
        if method is None:
            log.loge(_(f"Unknown method of message : {message}"))
            return log.return_error("Unknown method of message",{"error" : "method is missing"})
        # NOTE : If python version is above 3.10 , we can use "match" instead of "if elif"
        for case in switch(method):
            if case("RemoteConnected"):
                self._threadpool.set_tasks(self.remote_setup)
                break
            # NOTE: When use switch(), do not forget last break
            log.loge(_("No method matched"))
            break

    def on_send(self, message : dict) -> dict | None:
        """
            Send a message to client
            Args:
                message : dict
            Return:
                None
        """
        try:
            self._ws.send_message_to_all(json.dumps(message))
        except json.JSONDecodeError as exception:
            log.loge(_(f"Unknown format of message, error : {exception}"))
            return log.return_error("Unknown format of message",{"error" : exception})

    def remote_setup(self) -> dict:
        """
            Remote Setup Event
            Return the result of the remote server setup process
            Args: None
            ClientRequest:
                {
                    "event" : "RemoteServerSetup",
                    "uuid" : str,
                    "params" : None
                }
            Returns:
                dict:
                    {
                        "status" : "success","error","warning","debug"
                        "message" : str
                        "params" : None
                    }
            ClientReturn:
                {
                    "event" : "RemoteServerSetup",
                    "status" : "success","error","warning","debug"
                    "params" : {
                        "error" : str,
                        "debug" : str,
                        "message" : str,
                        "warning" : str
                    }
                }
            NOTE : This might be a little bit meaningless , if the connection is not established
                    how to send message to client
        """
        log.log(_(f"Remote server setup successfully"))
        res = {
            "event" : "RemoteServerSetup",
            "status" : "success",
            "params" : {
                "message" : "Remote server setup successfully"
            }
        }
        if self.on_send(res) is not None:
            log.logw(_("Some error occurred when sending message to client"))
            return log.return_error(_("Some error occurred when sending message to client"))
        return log.return_success("Remote server setup successfully")

    def remote_init(self , params : dict) -> dict:
        """
            Remote Init Event\n
            Return the result of the remote server init process
            Args:
                params : {
                    "timeout": int # timeout in seconds
                    "max_thread_num" : int # maximum number of concurrent threads
                    "debug" : bool # debug mode
                }
            ClientRequest:
                {
                    "event" : "RemoteInit",
                    "uuid" : str,
                    "params" : {
                        "timeout" : int,
                        "max_thread_num" : int,
                        "debug" : bool
                    }
                }
            Return:
                {
                    "status" : "success","error","warning","debug",
                    "message" : str,
                    "params" : {
                        "timeout" : int
                        "max_thread_num" : int
                        "debug" : bool
                    }
                }
            ClientReturn:
                {
                    "event" : "RemoteInit",
                    "status" : "success","error","warning","debug",
                    "params" : {
                        "message" : str,
                        "error" : str
                        "timeout" : int,
                        "max_thread_num" : int,
                        "debug" : bool
                    }
                }
        """
        def check_params(name : str , params : any,_type : type) -> bool:
            if params is not None:
                if isinstance(params,_type):
                    try:
                        exec(f"self._{name} = {params}")
                    except TypeError as exception:
                        log.logw(_(f"Invalid type, error : {exception}"))
                        return False
            return True
        flag = False
        flag = check_params("timeout", params.get("timeout"),int)
        flag = check_params("max_thread_num", params.get("max_thread_num"),int)
        flag = check_params("debug", params.get("debug"),bool)

        res = {
            "event" : "RemoteInit",
            "status" : "success",
            "params" : {
                "message" : "Remote server init successfully",
                "timeout" : self._info._timeout,
                "max_thread_num" : self._info._max_thread_num,
                "debug" : self._info._debug
            }
        }
        if flag is False:
            res = {
                "event" : "RemoteInit",
                "status" : "error",
                "params" : {
                    "message" : "Remote server init with error",
                    "error" : "Invalid parameters was given",
                }
            }
        else:
            log.log(_(f"Remote server init successfully"))
        if self.on_send(res) is not None:
            log.logw(_("Some error occurred when sending message to client"))
            return log.return_error(_("Some error occurred when sending message to client"))
        return log.return_success("Remote server init successfully")
         
    def remote_connect(self,params : dict) -> dict:
        """
            Remote Connect Event\n
            Return the result of the remote device connect process\n
            Args:
                params : {
                    "type": "telescope" # Is there any difference between "telescope" and "mount"
                    "name": str # The name of the telescope
                }
            ClientRequest:
                {
                    "event" : "RemoteConnect",
                    "uuid" : str,
                    "params" : {
                        "type" : str,
                        "name" : str,
                        # NOTE : If you want to connect to ASCOM or INDI telescope , you must give host and port
                        "info" : {
                            "host" : str,
                            "port" : int
                        }
                    }
                }
            Return: None
            ClientReturn:
                {
                    "event" : "RemoteConnect",
                    "status" : "success","error","warning","debug"
                    "params" : {
                        "message" : str,
                        "error" : str,
                        "info" : Telescope Info object
                    }
                }
        """
        if params.get("type") is None:
            res = {
                "event" : "RemoteConnect",
                "status" : "error",
                "params" : {
                    "message" : "Remote connect with error",
                    "error" : "Invalid parameters was given , not specified what type of telescope you want to connect to"
                }
            }
            if self.on_send(res) is not None:
                log.loge(_("Some error occurred when sending message to client"))
                return log.return_error(_("Some error occurred when sending message to client"))
            log.loge(_("No type specified"))
            return log.return_error("Invalid parameters type")
        
        _type = params.get("type")
        flag = False

        try:
            for case in switch(str(_type).lower()):
                if case("ascom"):
                    self._device = ascom()
                    res = self._device.connect(params.get("info").get("host"),params.get("info").get("port"),0)
                    if res.get("status") != "success":
                        log.loge(_(f"Error connecting to telescope , error : {res.get('message')}"))
                        return log.return_error(res.get("message"))
                    log.log(_("Connected to ASCOM telescope successfully"))
                    flag = True
                    break
                if case("indi"):
                    break
                log.loge(_(f"Unknown type of telescope was given , parameter : {_type}"))
                return log.return_error(_(f"Unknown type of telescope was given, parameter : {_type}"))
        except TypeError as exception:
            pass
        if flag is False:
            res = {
                "event" : "RemoteConnect",
                "status" : "error",
                "params" : {
                    "message" : "Remote connect to telescope with error",
                    "error" : ""
                }
            }
        else:
            res = {
                "event" : "RemoteConnect",
                "status" : "success",
                "params" : {
                    "message" : "Remote connect to telescope successfully",
                }
            }
        if self.on_send(res) is not None:
            log.loge(_("Some error occurred when sending message to client"))
            return log.return_error(_("Some error occurred when sending message to client"))
        self._info._connected = True
        return log.return_success("Remote connect successfully")

    def remote_disconnect(self) -> dict:
        """
            Remote disconnect event
            Return the result of the remote device disconnect process
            Args: None
            ClientRequest:
                {
                    "event" : "RemoteDisconnect",
                    "uuid" : str,
                    "params" : None
                }
            Return: 
                {
                    "status" : "success","error","warning","debug",
                    "message" : str
                    "params" : None
                }
            ClientReturn:
                {
                    "event" : "RemoteDisconnect",
                    "status" : "success","error","warning","debug"
                    "params" : {
                        "message" : str,
                        "error" : str,
                    }
                }
        """

    def remote_reconnect(self,params : dict) -> dict:
        """
            Remote reconnect event
            Return the result of the remote device reconnect process
            Args:
                {
                    "event" : "RemoteReconnect",
                    "uuid" : str,
                    "params" : None
                }
            ClientRequest:
                {
                    "event" : "RemoteReconnect",
                    "uuid" : str,
                    "params" : None
                }
            Return:
                {
                    "status" : "success","error","warning","debug",
                    "message" : str
                    "params" : None
                }
            ClientReturn
                {
                    "event" : "RemoteReconnect",
                    "status" : "success","error","warning","debug"
                }
        """


        