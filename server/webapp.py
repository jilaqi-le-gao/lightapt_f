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

from server.wsexception import WebAppSuccess as success
from server.wsexception import WebAppError as error
from server.wsexception import WebAppWarning as warning

from utils.utility import switch
from utils.lightlog import lightlog,DEBUG
log = lightlog(__name__)

import os,json,logging,uuid

from utils.i18n import _

from flask import Flask,render_template,redirect,Blueprint,request
from flask_login import LoginManager,login_required,login_user,logout_user,UserMixin
from werkzeug.security import check_password_hash,generate_password_hash

app = Flask(__name__,
    static_folder=os.path.join(os.getcwd(),"client","static"),
    template_folder=os.path.join(os.getcwd(),"client","templates")
)
app.secret_key = "lightapt"
auth = Blueprint("auth",__name__)
# Login system
login_system = LoginManager()
login_system.session_protection = "strong"
login_system.login_view = "login"
login_system.login_message_category = "info"
login_system.login_message = "Access denied."
login_system.init_app(app)

USERS = [
    {"id" : 1 ,"username": "admin", "password": generate_password_hash("admin")},
]

def create_user(user_name : str, password : str) -> None:
    """
        Create a new user | 创建一个新的用户
        Args:
            user_name: str
            password: str
    """
    user = {
        "name": user_name,
        "password": generate_password_hash(password),
        "id": uuid.uuid4()
    }
    USERS.append(user)

def get_user(user_name : str) -> UserMixin:
    """
        Get the user from the database
        Args:
            user_name: str
        Returns:
            UserMixin | None if the user is not available
    """
    for user in USERS:
        if user.get("username") == user_name:
            return user
    return None

@login_system.user_loader
def load_user(user_id : str):
    """
        Get the user from the database
        Args:
            user_id: str
        Returns:
            UserMixin | None if the user is not available
    """
    return User.get(user_id)

class User(UserMixin):
    """
        User Information object
    """
    def __init__(self, user):
        self.username = user.get("name")
        self.password_hash = user.get("password")
        self.id = user.get("id")

    def verify_password(self, password):
        """密码验证"""
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """获取用户ID"""
        return self.id

    @staticmethod
    def get(user_id):
        if not user_id:
            return None
        for user in USERS:
            if user.get('id') == user_id:
                return User(user)
        return None

@app.route("/login" , methods=["POST","GET"])
def login():
    """
        Login
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_info = get_user(username)
        if username is None or password is None:
            log.loge(_("Empty username or password"))
            return redirect("/login")
        if user_info is None:
            return redirect("/login")
        else:
            user = User(user_info)
            if user.verify_password(password):  # 校验密码
                login_user(user)
                log.log(_("User login successful"))
                return redirect('/desktop')
    return render_template('login.html')

@app.route("/login/" , methods=["POST","GET"])
def login_():
    return redirect('/login')

@app.route("/logout", methods=["POST","GET"])
def logout():
    logout_user()
    log.logd(_("User has been logged out"))
    return redirect('/')

@app.route("/logout/" , methods=["POST","GET"])
def logout_():
    return redirect('/logout')

# Disable Flask logging system
if not DEBUG:
    logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.ERROR)

config = None
config_path = "config.json"

camera_container = {}
mount_container = {}
focuser_container = {}
guider_container = {}
solver_container = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/camera')
@login_required
def camera():
    return render_template('camera.html')

@app.route('/camera/')
@login_required
def camera_():
    return redirect("/camera")
    
@app.route('/telescope')
@login_required
def telescope():
    return render_template('telescope.html')

@app.route('/telescope/')
@login_required
def telescope_():
    return redirect("/telescope")

@app.route('/focuser')
@login_required
def focuser():
    return render_template('focuser.html')

@app.route('/focuser/')
@login_required
def focuser_():
    return redirect("/focuser")

@app.route('/guider')
@login_required
def guider():
    return render_template('guider.html')

@app.route('/guider/')
@login_required
def guider_():
    return redirect("/guider")

@app.route('/solver')
@login_required
def solver():
    return render_template('solver.html')

@app.route('/solver/')
@login_required
def solver_():
    return redirect("/solver")
    
@app.route('/novnc')
@login_required
def novnc():
    return render_template('novnc.html')

@app.route('/novnc/')
@login_required
def novnc_():
    return redirect("/novnc")

@app.route('/client')
@login_required
def client():
    return render_template('client.html')

@app.route('/client/')
@login_required
def client_():
    return redirect("/client")

@app.route('/desktop')
@login_required
def desktop():
    return render_template('desktop.html')

@app.route('/desktop/')
@login_required
def desktop_():
    return redirect("/desktop")

@app.route("/ndesktop")
def ndesktop():
    return render_template('ndesktop.html')

@app.route("/ndesktop/")
def ndesktop_():
    return redirect("/ndesktop")

@app.route("/editor")
@login_required
def editor():
    return render_template('jsoneditor.html')

@app.route("/editor/")
@login_required
def editor_():
    return redirect("/editor")

@app.route("/skymap")
@login_required
def skymap():
    return render_template('skymap.html')

@app.route("/skymap/")
@login_required
def skymap_():
    return redirect("/skymap")

@app.route("/scripteditor")
@login_required
def scripteditor():
    return render_template('scripteditor.html')

@app.route("/scripteditor/")
@login_required
def scripteditor_():
    return redirect("/scripteditor")
    
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

@app.route("/config",methods = ["GET"])
@login_required
def get_config():
    if not os.path.exists("config"):
        return {
            "error" : error.ConfigFolderNotFound.value
        }
    if not os.path.exists(os.path.join("config",config_path)):
        return {
            "error" : error.ConfigFileNotFound.value
        }
    try:
        with open(os.path.join("config",config_path),mode="r",encoding="utf-8") as file:
            try:
                config = json.load(file)
                return {
                    "config" : config
                }
            except json.JSONDecodeError as e:
                log.loge(error.LoadConfigFailed.value.format(e))
                return {
                    "error" : error.LoadConfigFailed.value,
                    "exception" : str(e)
                }
    except OSError as e:
        return {
            "error" : str(e)
        }

@app.route("/config/",methods = ["GET"])
@login_required
def get_config_():
    return redirect('/config')

@app.route("/device",methods = ["GET"])
@login_required
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
    _path = os.path.join(os.getcwd(),"config","client")
    if not os.path.exists(_path):
        return {
            "error": error.ConfigFolderNotFound.value
        }
    for device in os.listdir(_path):
        device_name = device.split(".")[0]
        try:
            with open(os.path.join(_path,device),mode="r",encoding="utf-8") as device:
                if device is None:
                    log.loge(error.EmptyConfigFile)
                    break
                try:
                    device_list[device_name] = {}
                    tmp = json.load(device)
                    device_list[device_name]["host"] = tmp.get("host")
                    device_list[device_name]["port"] = tmp.get("port")
                    device_list[device_name]["type"] = tmp.get("type")
                except json.JSONDecodeError as e:
                    log.loge(error.InvalidFile.value.format(e))
                    return {
                        "error" : error.InvalidFile.value,
                        "exception" : str(e)
                    }
        except OSError as e:
            log.loge(error.LoadConfigFailed.value.format(e))
            return {
                "error" : error.LoadConfigFailed.value,
                "exception" : str(e)
            }
    return device_list

@app.route("/device/",methods = ["GET"])
@login_required
def get_device_():
    return redirect("/device")

@app.route("/device/<device_type>/<device_id>",methods=["GET"])
@login_required
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
            "error": error.InvalidDeviceID.value
        }
    device_config = {}
    if device_type not in ["camera","mount","focuser","guider","solver"]:
        return {
            "error": error.InvalidDeviceType.value
        }
    _path = os.path.join(os.path.join(os.getcwd(),os.path.join("config",device_type)),device_id+".json")
    if os.path.exists(_path):
        try:
            with open(_path,mode="r",encoding="utf-8") as file:
                try:
                    device_config = json.load(file)
                except json.JSONDecodeError as e:
                    log.loge(error.LoadConfigFailed.value.format(e))
                    return {
                        "error" : error.LoadConfigFailed.value,
                        "expetion" : str(e)
                    }
        except OSError as e:
            log.loge(error.LoadConfigFailed.value.format(e))
            return {
                "error" : error.LoadConfigFailed.value,
                "exception" : str(e)
            }
        return device_config
    return {
        "error" : error.ConfigFileNotFound.value,
    }

@app.route("/device/<device_type>/<device_id>/",methods=["GET"])
@login_required
def device_id_(device_type, device_id):
    return redirect(f"/device/{device_type}/{device_id}")

@app.route("/start/<script>", methods=["GET"])
@login_required
def start_device(script):
    """
        Start device | 启动服务器
        Args:
            script : file path to script
        Returns:
            status : dict
    """
    if script is None:
        return {
            "error": error.InvalidScriptPath.value
        }
    _path = os.path.join("config", script)
    if not os.path.exists(_path):
        return {
            "error" : error.ScriptNotFound.value
        }
    device_type = None
    device_host = None
    device_port = None
    device_debug = None
    device_threaded = None
    start_script = None
    try:
        with open(_path,mode="r",encoding="utf-8") as file:
            try:
                start_script = json.load(file)
            except json.JSONDecodeError as e:
                log.loge(error.LoadScriptFailed.value.format(e))
                return {
                    "error" : error.LoadScriptFailed.value,
                    "exception" : str(e)
                }
            device_type = start_script.get("type")
            log.logd(_("Device type : {}").format(device_type))
            device_host = start_script.get("host")
            log.logd(_("Device host : {}").format(device_host))
            device_port = start_script.get("port")
            log.logd(_("Device port : {}").format(device_port))
            device_debug = start_script.get("debug")
            log.logd(_("Device debug : {}").format(device_debug))
            device_threaded = start_script.get("threaded")
            log.logd(_("Device threaded : {}").format(device_threaded))
    except OSError as e:
        log.loge(error.LoadConfigFailed.value.format(e))
        return {
            "error" : error.LoadConfigFailed.value,
            "exception" : str(e)
        }
    if device_type not in ["camera","mount","focuser","guider","sovlver"]:
        log.loge(error.InvalidDeviceType)
        return {
            "error" : error.InvalidDeviceType.value
        }
    # TODO : There needs well consideration
    for case in switch(device_type):
        if case("camera"):
            global camera_container
            if device_id in camera_container.keys():
                log.logw(error.HadAlreadyStartedSame.value)
                return {
                    "error" : error.HadAlreadyStartedSame.value
                }
            camera_container[device_id] = {}
            camera_container[device_id]["class"] = wscamera(device_type,device_id,device_host,device_port,device_debug,device_threaded,{})
            camera_container[device_id]["host"] = device_host
            camera_container[device_id]["port"] = device_port
            camera_container[device_id]["debug"] = device_debug
            camera_container[device_id]["threaded"] = device_threaded
            print(camera_container)
            log.log(success.DeviceStartedSuccess)
            return {
                "message" : success.DeviceStartedSuccess.value
            }
        if case("mount"):
            global mount_container
            if device_id in mount_container.keys():
                log.logw(error.HadAlreadyStartedSame.value)
                return {
                    "error" : error.HadAlreadyStartedSame.value
                }
            mount_container[device_id] = {}
        if case("focuser"):
            global focuser_container
            if device_id in focuser_container.keys():
                log.logw(error.HadAlreadyStartedSame.value)
                return {
                    "error" : error.HadAlreadyStartedSame.value
                }
            focuser_container[device_id] = {}
            break
        if case("guider"):
            global guider_container
            if device_id in guider_container.keys():
                log.logw(error.HadAlreadyStartedSame.value)
                return {
                    "error" : error.HadAlreadyStartedSame.value
                }
            guider_container[device_id] = {}
            break
        if case("solver"):
            global solver_container
            if device_id in solver_container.keys():
                log.logw(error.HadAlreadyStartedSame.value)
                return {
                    "error" : error.HadAlreadyStartedSame.value
                }
            solver_container[device_id] = {}
            break
        break
    return {
        "error" : error.InvalidDeviceType.value
    }

@app.route("/stop/<device_type>/<device_id>",methods=["GET"])
@login_required
def stop_device(device_type, device_id):
    """
        Stop device and shutdown the server via http request
        Args: 
            device_type : str # type of device
            device_name : str # name of device
        Returns: None
    """
    if device_type not in ["camera","mount","focuser","solver","guider"]:
        log.loge(error.InvalidDeviceType)
        return {
            "error" : error.InvalidDeviceType.value
        }
    for case in (device_type):
        if case("camera"):
            global camera_container
            if device_id not in camera_container.keys():
                log.logw(error.DeviceNotStarted)
                return {
                    "error" : error.DeviceNotStarted.value
                }
            res = camera_container[device_id]["class"].disconnect()
            if res.get('status') != 0:
                log.logw(error.DeviceStopFailed)
                return {
                    "error" : error.DeviceStopFailed.value,
                    "status" : res.get('status'),
                    "message" : res.get('message')
                }
            camera_container[device_id]["class"] = None
            log.log(success.DeviceStoppedSuccess)
            return {
                "success" : success.DeviceStoppedSuccess.value
            }
        if case("mount"):
            global mount_container
            if device_id not in mount_container.keys():
                log.logw(error.DeviceNotStarted)
                return {
                    "error" : error.DeviceNotStarted.value
                }
            res = mount_container[device_id]["class"].disconnect()
            if res.get('status')!= 0:
                log.logw(error.DeviceStopFailed)
                return {
                    "error" : error.DeviceStopFailed.value,
                    "status" : res.get('status'),
                    "message" : res.get('message')
                }
            mount_container[device_id]["class"] = None
            log.log(success.DeviceStoppedSuccess)
            return {
                "success" : success.DeviceStoppedSuccess.value
            }
        if case("focuser"):
            global focuser_container
            if device_id not in focuser_container.keys():
                log.logw(error.DeviceNotStarted)
                return {
                    "error" : error.DeviceNotStarted.value
                }
            res = focuser_container[device_id]["class"].disconnect()
            if res.get('status')!= 0:
                log.logw(error.DeviceStopFailed)
                return {
                    "error" : error.DeviceStopFailed.value,
                    "status" : res.get("status"),
                    "message" : res.get("message")
                }
            focuser_container[device_id]["class"] = None
            log.log(success.DeviceStoppedSuccess)
            return {
                "success" : success.DeviceStoppedSuccess.value
            }

@app.route("/restart/<deivce_type>/<device_id>", methods=["GET"])
@login_required
def restart_device(device_type,device_id):
    """
        Restart a device via http request 
        Args: 
            device_id : str
        Returns: None
    """
    if device_type not in ["camera","mount","focuser","solver","guider"]:
        log.loge(error.InvalidDeviceType)
        return {
            "error" : error.InvalidDeviceType.value
        }
    for case in (device_type):
        if case("camera"):
            global camera_container
            if device_id not in camera_container.keys():
                log.logw(error.DeviceNotStarted)
                return {
                    "error" : error.DeviceNotStarted.value
                }
            res = camera_container[device_id]["class"].reconnect()
            if res.get('status')!= 0:
                log.logw(error.DeviceRestartFailed)
                return {
                    "error" : error.DeviceRestartFailed.value,
                    "status" : res.get('status'),
                    "message" : res.get('message')
                }
            break
        if case("mount"):
            global mount_container
            if device_id not in mount_container.keys():
                log.logw(error.DeviceNotStarted)
                return {
                    "error" : error.DeviceNotStarted.value
                }
            res = mount_container[device_id]["class"].reconnect()
            if res.get('status')!= 0:
                log.logw(error.DeviceRestartFailed)
                return {
                    "error" : error.DeviceRestartFailed.value,
                    "status" : res.get('status'),
                    "message" : res.get('message')
                }
            break
        if case("focuser"):
            global focuser_container
            if device_id not in focuser_container.keys():
                log.logw(error.DeviceNotStarted)
                return {
                    "error" : error.DeviceNotStarted.value
                }
            res = focuser_container[device_id]["class"].reconnect()
            if res.get('status')!= 0:
                log.logw(error.DeviceRestartFailed)
                return {
                    "error" : error.DeviceRestartFailed.value,
                    "status" : res.get('status'),
                    "message" : res.get('message')
                }
            break
        if case("solver"):
            global solver_container
            if device_id not in solver_container.keys():
                log.logw(error.DeviceNotStarted)
                return {
                    "error" : error.DeviceNotStarted.value
                }
            res = solver_container[device_id]["class"].reconnect()
            if res.get('status')!= 0:
                log.logw(error.DeviceRestartFailed)
                return {
                    "error" : error.DeviceRestartFailed.value,
                    "status" : res.get('status'),
                    "message" : res.get('message')
                }
            break
        if case("guider"):
            global guider_container
            if device_id not in guider_container.keys():
                log.logw(error.DeviceNotStarted)
                return {
                    "error" : error.DeviceNotStarted.value
                }
            res = guider_container[device_id]["class"].reconnect()
            if res.get('status')!= 0:
                log.logw(error.DeviceRestartFailed)
                return {
                    "error" : error.DeviceRestartFailed.value,
                    "status" : res.get('status'),
                    "message" : res.get('message')
                }
            break
        break
    return {
        "success" : success.DeviceRestartSuccess.value
    }

@app.route("/scan/<device_type>/<device>",methods = ["GET"])
@login_required
def scan_device(device_type,device):
    """
        Scan a device via http request 
        Args: 
            device_type : str
        Returns: None
    """
    if device_type not in ["camera","mount","focuser","solver","guider"]:
        log.loge(error.InvalidDeviceType)
        return {
            "error" : error.InvalidDeviceType.value
        }
    for case in (device_type):
        if case("camera"):
            if device not in ["ascom","indi","asi","qhy"]:
                log.loge(error.InvalidDeviceType)
                return {
                    "error" : error.InvalidDeviceType.value
                }
            break
        if case("mount"):
            if device not in ["ascom","indi","ioptron"]:
                log.loge(error.InvalidDeviceType)
                return {
                    "error" : error.InvalidDeviceType.value
                }
            break
        if case("focuser"):
            break
        if case("solver"):
            break
        if case("guider"):
            break
        break

@app.route("/start/<script>/",methods=["GET"])
@login_required
def start_device_(script):
    return redirect("/start/<script>")

@app.route("/stop/<device_type>/<device_id>/",methods=["GET"])
@login_required
def stop_device_(device_type, device_id):
    return redirect("/stop/<device_type>/<device_name>")

@app.route("/restart/<deivce_type>/<device_id>/",methods=["GET"])
@login_required
def restart_device_(device_type,device_id):
    return redirect("/restart/<device_type>/<device_id>")

@app.route("/scan/<device_type>/<device>/",methods=["GET"])
@login_required
def scan_device_(device_type,device):
    return redirect("/scan/<device_type>/<device>")

@app.route("/setconfig/<config_path>", methods=["GET"])
@login_required
def set_config(config_path):
    """
        Set the configuration file path | 设置配置文件路径
        Args:
            config_path : str
        Returns:
            status : dict
    """
    if config_path is None:
        return {
            "error" : error.InvalidFile.value
        }
    if not os.path.exists(config_path):
        return {
            "error" : error.InvalidFile.value
        }
    try:
        with open(config_path,mode="r",encoding="utf-8") as file:
            try:
                global config
                config = json.load(file)
            except json.JSONDecodeError as e:
                log.loge(error.LoadConfigFailed)
                return {
                    "error" : error.LoadConfigFailed.value,
                    "exception" : str(e)
                }
    except OSError as e:
        return {
            "error" : _("OS Error : {}").format(e)
        }
    return {
        "config" : config
    }

@app.route("/setconfig/<config_path>/", methods=["GET"])
@login_required
def set_config_(config_path):
    return redirect("/setconfig/<config_path>")

def set_configration(config_path : str) -> None:
    """
        Set configration | 设置
        Args:
            config_path : str # path to the configuration file
            start_script : str # path to the script to run 
        Returns:
            None
    """
    if config_path is None or config_path == "":
        log.logd(_("No configuration file is specified , use default configuration"))
        config_path = os.path.join("config",config_path)
    log.logd(_("Trying to load configuration file : {}").format(config_path))
    if not os.path.exists(config_path):
        log.loge(_("Could not find config file : {}").format(config_path))
        return
    try:
        with open(config_path,mode="r",encoding="utf-8") as file:
            try:
                global config
                config = json.load(file)
                if config.get('host') is None or config.get('port') is None:
                    log.loge(_("Configuration is missing from the configuration file"))
                    return 
                log.logd(_("Configuration host : {}").format(config.get('host')))
                log.logd(_("Configuration port : {}").format(config.get('port')))
                log.logd(_("Configuration debug : {}").format(config.get('debug')))
                log.logd(_("Configuration threaded : {}").format(config.get('threaded')))
            except json.JSONDecodeError as e:
                log.loge(_("Error decoding config file : {}").format(e))
                return
    except OSError as e:
        log.loge(_("Faild to load config file, error : {}").format(e))
        return

@app.route("/script/<script_name>")
def load_script(script_name):
    """
        Load a script
        Args:
            script_name : str
        Returns:
            status : dict
    """
    if script_name is None:
        return {
            "error" : error.EmptyScriptFile.value
        }
    if not os.path.exists(script_name):
        return {
            "error" : error.InvalidScriptPath.value
        }
    
    
def run_server(host : str , port : int , threaded = True , debug = False) -> None:
    """
        Start the server | 启动服务器
        Args: 
            host : str # default is "127.0.0.1"
            port : int # default is 5000
            threaded : bool # default is False
            debug : bool # default is False
        Return: None
    """
    if config is None:
        _host = host if host is not None else "127.0.0.1"
        _port = port if port is not None else 5000
        _threaded = threaded if threaded is not None else False
        _debug = debug if debug is not None else False
    else:
        _host = config.get('host')
        _port = config.get('port')
        _threaded = config.get('threaded')
        _debug = config.get('debug')
    if _debug is True:
        log.log(_("Running debug web server on {}:{}").format(_host,_port))
        app.run(host=_host, port=_port,debug=True)
    else:
        log.log(_("Running web server on {}:{}").format(_host,_port))
        app.run(host=_host, port=_port,threaded=_threaded)
        
