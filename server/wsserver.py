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

from utils.utility import switch
from utils.lightlog import lightlog
log = lightlog(__name__)
import json
import logging
import gettext
_ = gettext.gettext

from flask import Flask,render_template
from websocket_server import WebsocketServer
from server.wscamera import wscamera as camera
from server.wstelescope import wstelescope as telescope
from server.wsfocuser import wsfocuser as focuser
from server.wsguider import wsguider as guider

app = Flask(__name__)
thread = None
server = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/main.html')
def main():
    return render_template('main.html')

class wsserver(object):
    """
        Main Websocket Server Class based on websocket_server.
        All comunication are finish here.
        So this is the core part of the LightAPT
        NOTE : Finish this first
    """

    def remote_setdashboardmode(self):
        """
            Set the dashboard mode 
            Args : None
            Returns : None
            Send : {
                "result" : 1
                "code" : error code # default is None
                "Event" : event
                "AIRVersion" : current version of LightAPT
            }
        """
        result = {
            "result" : "1",
            "code" : "",
            "Event" : "Version",
            "AIRVersion" : "2.0.0"
        }
        server.send_message_to_all(json.dumps(result))

ws_class = wsserver()

def parser_json(message : str) -> None:
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
        if case("RemoteSetDashboardMode"):
            ws_class.remote_setdashboardmode()
            break
        break
    
def on_connect(client, server) -> None:
    """
        Callback function for websocket connection
        Args:
            None
        Return:
            None
    """
    log.log(_("Established websocket connection with client successfully"))

def on_disconnect(client, server) -> None:
    """
        Callback function for websocket disconnection
        Args:
            None
        Return:
            None
    """
    log.log(_("Disconnected websocket client successfully"))

def on_message(client, server, message) -> None:
    """
        On message callback function | 获取客户端信息
        Args : 
            None
        Return:
            None
    """
    log.logd(_(f"Client({client['id']}) responded : {message}"))
    if not isinstance(message , str) : 
        log.loge(_("Unknown message format , please"))
    parser_json(message)

def run_server(host : str , port : int) -> None:
    """
        Start the server | 启动服务器
        Args: None
        Return: None
    """
    app.run(host=host, port=port)

def run_ws_server(host : str , port : int) -> None:
    """
        Start websocket server | 启动Websocket服务器
        Args: None
        Return: None
    """
    global server
    server = WebsocketServer(host = host , port = port , loglevel=logging.DEBUG)
    server.set_fn_new_client(on_connect)
    server.set_fn_client_left(on_disconnect)
    server.set_fn_message_received(on_message)
    server.run_forever()  
    
