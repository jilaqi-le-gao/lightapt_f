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

from server.wscamera import wscamera

from utils.utility import switch
from utils.lightlog import lightlog
log = lightlog(__name__)

import os,json,threading
import gettext
_ = gettext.gettext

from flask import Flask,render_template,redirect

app = Flask(__name__,
    static_folder=os.path.join(os.getcwd(),os.path.join("client","static")),
    template_folder=os.path.join(os.getcwd(),os.path.join("client","templates"))
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/main.html')
def main():
    return render_template('main.html')

@app.route('/camera')
def camera():
    return render_template('camera.html')
    
@app.route('/telescope')
def telescope():
    return render_template('telescope.html')

@app.route('/focuser')
def focuser():
    return render_template('focuser.html')

@app.route('/guider')
def guider():
    return render_template('guider.html')

@app.route('/solver')
def solver():
    return render_template('solver.html')
    
@app.route('/novnc')
def novnc():
    return render_template('novnc.html')

@app.route('/client')
def client():
    return render_template('client.html')

@app.route("/config",methods = ["GET"])
def get_config():
    if not os.path.exists("config"):
        return {
            "error" : "Could not find configration folder"
        }
    if not os.path.exists(os.path.join("config","config.json")):
        return {
            "error" : "Could not find configration file"
        }
    try:
        with open(os.path.join("config","config.json"),mode="r",encoding="utf-8") as file:
            config = json.load(file)
            return {
                "config" : config
            }
    except OSError as e:
        return {
            "error" : str(e)
        }

@app.route("/config/",methods = ["GET"])
def get_config_():
    return redirect('/config')

@app.route("/device",methods = ["GET"])
def device():
    """
        Returns a dict of devices and their configurations | 返回设备列表以及对应配置
        Args : None
        Returns :
            device_list : dict
            {
                "device_name" : {
                    "host" : str, # default is "127.0.0.1",
                    "port" : int  # default is 8000
                }
            }
    """
    device_list = {}
    _path = os.path.join(os.getcwd(),os.path.join("config","client"))
    if not os.path.exists(_path):
        return {
            "error": "Could not find device configuration folder"
        }
    for device in os.listdir(_path):
        device_name = device.split(".")[0]
        try:
            with open(os.path.join(_path,device),mode="r",encoding="utf-8") as device:
                if device is None:
                    log.loge(_(f"Empty device configuration file : {device}"))
                    break
                try:
                    device_list[device_name] = {}
                    tmp = json.load(device)
                    device_list[device_name]["host"] = tmp.get("host")
                    device_list[device_name]["port"] = tmp.get("port")
                    device_list[device_name]["type"] = tmp.get("type")
                except json.JSONDecodeError as e:
                    log.loge(_(f"Invalid device configuration file : {device}"))
        except OSError as e:
            log.loge(_(f"Faild to load device configuration , error : {e}"))
    return device_list

@app.route("/device/",methods = ["GET"])
def get_device_():
    return redirect("/device")

@app.route("/device/<device_type>/<device_id>",methods=["GET"])
def device_id(device_type,device_id):
    """
        Read device configuration | 读取设备配置
        Args :
            device_type : str # type of device
            device_id : str # device id
        Returns :
            device_config : dict
    """
    if device_id is None:
        return {
            "error": "Invalid device id"
        }
    device_config = {}
    if device_type not in ["camera","mount","focuser","guider","solver"]:
        return {
            "error": "Invalid device type"
        }
    _path = os.path.join(os.path.join(os.getcwd(),os.path.join("config",device_type)),device_id+".json")
    if os.path.exists(_path):
        try:
            with open(_path,mode="r",encoding="utf-8") as file:
                device_config = json.load(file)
        except OSError as e:
            log.loge(_(f"Faild to load device configuration, error : {e}"))
        return device_config
    return {
        "error" : _("Could not find device configuration"),
    }

@app.route("/device/<device_type>/<device_id>/")
def device_id_(device_type, device_id):
    return redirect(f"/device/{device_type}/{device_id}")

@app.route("/start/<device_type>/<device_id>/<device_host>/<device_port>", methods=["GET"])
def start_device(device_type,device_id, device_host, device_port):
    """
        Start device | 启动服务器
        Args:
            device_type : str # type of device
            device_id : str # id of the device
            device_host : str # host of the device , default is "127.0.0.1"
            device_port : int # port of the device , default is 8000
        Returns:
            status : dict
    """
    if device_type is None or device_id is None or device_host is None or device_port is None:
        log.loge(_("Please provide enough information"))
        return {
            "error" : _("Please provide enough information")
        }
    if device_type not in ["camera","mount","focuser","guider","sovlver"]:
        log.loge(_("Unknown device type"))
        return {
            "error" : _("Unknown device type")
        }
    # TODO : There needs well consideration
    for case in switch(device_type):
        if case("camera"):
            
            break
        if case("mount"):
            break
        if case("focuser"):
            break
        if case("guider"):
            break
        if case("solver"):
            break
        break
    
def run_server(host : str , port : int , threaded : bool , debug = False) -> None:
    """
        Start the server | 启动服务器
        Args: 
            host : str # default is "127.0.0.1"
            port : int # default is 5000
            threaded : bool # default is False
            debug : bool # default is False
        Return: None
    """
    if host is None:
        host = "127.0.0.1"
    if port is None:
        port = 5000
    if threaded is None:
        threaded = True
    if debug is None:
        debug = False
    app.run(host=host, port=port,debug=True)
