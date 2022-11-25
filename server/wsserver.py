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
log = lightlog(__name__)
import json
import gettext
_ = gettext.gettext

from flask import Flask,render_template
from flask_socketio import SocketIO,emit

from server.wscamera import wscamera as camera
from server.wstelescope import wstelescope as telescope
from server.wsfocuser import wsfocuser as focuser
from server.wsguider import wsguider as guider

app = Flask(__name__)
socketio = SocketIO(app)

IP_Address = '127.0.0.1'
IP_Port = 5000

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/main.html')
def main():
    return render_template('main.html')

@socketio.on('connect', namespace='/lightapt')
def on_connect():
    """
        Initialize the connection with the client | 初始化与服务器的连接
        Args: None
        Return: None
    """
    

@socketio.on('disconnect', namespace='/lightapt')
def on_disconnect():
    """
        Disconnect the client | 断开客户端的连接
        Args: None
        Return: None
    """
    

@socketio.on('json')
def on_message(data):
    """"
        Receive message from the client | 获取客户端信息
        Args:
            data:
        Return:
            None
    """
    log.logd(_(f"Receive message from client : {str(data)}"))
    parser_json(data)

def return_error(info : str,params : dict) -> dict :
    """
        Return error message to the client | 获取客户端信息
        Args:
            info: str # Info message
            params : dict # Container
        Return:
            None
    """
    r = {
        "status" : "error",
        "message" : info,
        "params" : params
    }
    return r

def return_warning(info : str,params : dict) -> dict:
    """
        Return warning message to the client | 获取客户端信息
        Args:
            info: str # Info message
            params : dict # Container
        Return:
            None
    """
    r = {
        "status" : "warning",
        "message" : info,
        "params" : params
    }
    return r


def parser_json(message) -> None:
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
        return return_error("Unknown format of message",{"error" : exception})
    method = data.get("method")
    if method is None:
        log.loge(_(f"Unknown method of message : {message}"))
        return return_error("Unknown method of message",{"error" : "method is missing"})
    





def run_server() -> None:
    """
        Start the server | 启动服务器
        Args: None
        Return: None
    """
    socketio.run(app, host=IP_Address, port=IP_Port,debug=True)

class ws_device_info():
    """Websocket device infomation class"""

    """Property Info"""
    _device_name : str
    _device_id : int
    _device_type : str

    _command : list

    """Status Info"""
    _is_connected = False
    _is_operating = False

class wsserver():
    """Websocket Class"""

    def __init__(self) -> None:
        """Initialize"""
        self.app = app
        self.socketio = socketio
        self.device = None

    def __del__(self) -> None:
        """Destructor"""

    def connect(self,parmas : dict) -> dict:
        """
            Connect to the device | 连接设备
            Args:
                parmas : {
                    "type" : str # "
                    "name" : str # Device name you want to connect to
                    "id" : int # Id of the device
                    "debug" : bool # True if you want to debug
                }
            Return:
                dict:
                    "status" : str
                    "message" : str
                    "params" : Container
        """

    def disconnect(self,params : dict) -> dict:
        """
            Disconnect from the device | 与设备断开连接
            Args:
                params : None
                dict:
                    "status" : str
                    "message" : str
                    "params" : Container
        """

    def update_config(self) -> dict:
        """
            Update device configuration | 获取设备信息
            Args:
                None
            Return:
                dict:
                    "status" : str
                    "message" : str                    
                    "params" : Container
        """
    
    def scan_command(self) -> dict:
        """
            Scan command | 获取设备支持的命令
            Args:
                None
            Return:
                dict:
                    "status" : str
                    "message" : str
                    "params" : {
                        "type" : str # Device type
                        "command" : dict
                    }
            Note : This function should be called when after update_config() called
        """
    
    def check_command_support(self,params : dict) -> dict:
        """
            Check command support | 检查命令是否支持
            Args:
                params : {
                    "command" : list
                }
            Return:
                dict:
                    "status" : str
                    "message" : str
        """

    def run_command(self,params : dict) -> dict:
        """
            Run command on device | 运行命令
            Args:
                params : None
                dict:
                    "status" : str
                    "message" : str
                    "params" : {
                        "error" : error message
                    }
        """

    
    
