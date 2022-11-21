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
from driver.basicfilterwheel import (BasicFilterwheel,FilterwheelInfo)
from libs.alpyca.filterwheel import (FilterWheel)
from libs.alpyca.exceptions import (DriverException,
                                    NotConnectedException,
                                    NotImplementedException)
log = lightlog(__name__)

import os
from time import sleep
from requests.exceptions import ConnectionError
from yaml import (safe_load,safe_dump)
import gettext
_ = gettext.gettext

class filterwheel(BasicFilterwheel):
    """ASCOM Filterwheel class"""

    def __init__(self) -> None:
        """Constructor"""
        self.info = FilterwheelInfo()
        self.device = None
        log.log(_("Initializing ascom filterwheel object"))

    def __del__(self) -> None:
        """Destructor"""
        if self.info._is_connected:
            r = self.disconnect({})
            if r.get("status") != "success":
                log.loge(_("Failed to delete ascom filterwheel object"))
        self.device = None
        log.log(_("Successfully deleted ascom filterwheel object"))

    def connect(self,params : dict) -> dict:
        """
            Connect to ASCOM filterwheel
            Args:
                params: {
                    "host" : "127.0.0.1",
                    "port" : 11111,
                    "device_number" : int # default is 0
                }
            Returns:
                {
                    "status" : " "success","error","warning","debug"
                    "message" : "ASCOM filterwheel is connected" # success
                                "Faild to connect to ASCOM filterwheel" # error
                                "ASCOM filterwheel is connected with warning" # warning
                    "params" : {
                        "name" : str
                        "info" : filterwheelInfo object
                    }
                }
        """
        host = params.get("host")
        port = params.get("port")
        device_number = params.get("device_number")
        # Check if the parameters is legal | 检查输入是否合法
        if not isinstance(host, str) or not isinstance(device_number,int) or not isinstance(port, int):
            log.loge(_("Invalid parameters when executing connect function"))
            return self.return_message("error",_("Invalid parameters when executing connect function"))
        ip_address = host + ":" + str(port)
        # Connect to ASCOM Remote Server | 连接ASCOMRemote服务器
        try:
            self.device = FilterWheel(ip_address,device_number)
            self.device.Connected = True
            self.info._is_connected = True
        except DriverException as exception:
            log.loge(_(f"Failed to connect to filterwheel , error: {exception}"))
            return self.return_message("error",_("Failed to connect to filterwheel"),{"error": exception})
        except ConnectionError as exception:
            log.loge(_(f"Remote connection error: {exception}"))
            return self.return_message("error",_("Remote connection error"),{"error": exception})
        log.log(_("Connected to filterwheel successfully"))
        # Update filterwheel Infomation | 更新滤镜轮信息
        res = self.update_config()
        if res.get("status") != "success":
            return res
        r = {
            "name" : self.info._name,
            "info" : res.get("params")
        }
        return self.return_message("success",_("Connected to filterwheel successfully"),r)

    def disconnect(self, params : dict) -> dict:
        """
            Disconnect from ASCOM filterwheel
            Args:
                params: {
                    "name" : str
                }
            Returns:
                {
                    "status" : " "success","error","warning","debug"
                    "message" : "Disconnect from ASCOM filterwheel successfully" # success
                                "Faild to disconnect from ASCOM filterwheel" # error
                                "ASCOM filterwheel is disconnected with warning" # warning
                    "params" : {
                        "error" : error message # usually exception
                    }
                }
            Note : Must disconnect from filterwheel when destory self !
        """
        log.log(_("Try to disconnect from ASCOM filterwheel"))
        name = params.get("name")
        try:
            self.device.Connected = False
            self.info._is_connected = False
        except DriverException as e:
            log.loge(_("Failed to disconnect from filterwheel , error : %s"),e)
            return self.return_message("error",_("Failed to disconnect from ASCOm filterwheel"),{"error" : exception})
        except ConnectionError as exception:
            log.loge(_(f"Remote connection error: {exception}"))
            return self.return_message("error",_("Remote connection error"),{"error" : exception})
        log.log(_("Disconnect from ASCOM filterwheel successfully"))
        return self.return_message("success",_("Disconnect from ASCOM filterwheel successfully"),{})

    def update_config(self) -> dict:
        """
            Update configuration of ASCOM filterwheel
            Returns:
                {
                    "status" : "success","error","warning","debug"
                    "message" : "Update configuration successfully" # success
                                "Faild to update configuration" # error
                                "ASCOM configuration is updated with warning" # warning
                    "params" : {
                        "info" : filterwheelInfo object (use get_dict())
                        "error" : error message # usually exception
                    }
                }
            Note : This function is usually run when initialize the filterwheel
        """
        log.log(_("Update ASCOM filterwheel configuration"))
        try:
            """Get basic information | 获取基础信息"""
            self.info._address = self.device.address
            self.info._name = self.device.Name
            self.info._api_version = self.device.api_version
            self.info._id = self.device._client_id
            self.info._description = self.device.Description
            """Get properties information | 获取配置信息"""
            self.info._filter_info = self.device.Names
            self.info._current_position = self.device.Position
            self.info._offset_filter = self.device.FocusOffsets
            """Set configuration file name | 设置配置文件名称默认为设备名称"""
            self.info._config_file = self.device.Name
        except NotConnectedException as exception:
            log.loge(_("No filterwheel connected , please connect to filterwheel before run update_config()"))
            return self.return_message("error", _("No filterwheel connected"),{"error" : exception})
        except DriverException as exception:
            log.loge(_("filterwheel driver error , when run update_config()"))
            return self.return_message("error", _("filterwheel driver error"),{"error" : exception})
        except ConnectionError as exception:
            log.loge(_("Remote server connection error, when run update_config()"))
            return self.return_message("error",_("Remote connection error"),{"error" : exception})
        
        log.log(_("Update filterwheel configuration successfully"))
        return self.return_message("success", _("Update filterwheel configuration successfully"),self.info.get_dict())

    def load_config(self, params: dict) -> dict:
        """
            Load configuration from file | 从文件中加载配置
            Args:
                {
                    "filename": filename,
                    "path": path,
                }
            Return:
                {
                    "status": "success","error","warning","debug"
                    "message" : str
                    "params" : configuration load from file
                }
        """
        path = os.path.join(params.get("path"), params.get("filename"))
        if not os.path.isfile(path):
            log.loge(_("Faild to load configuration file %(path)s"))
            return self.return_message("error", _("Faild to load configuration file %(path)"),{})
        with open(path, mode = 'r', encoding="utf-8") as file:
            config = safe_load(file)
            
    def save_config(self) -> dict:
        """
            Save the configuration file | 保存配置文件
            Return:
                {
                    "status" : "success","error","warning","debug"
                    "message" : str
                    "params" : {
                        "error" : exception
                    }
                }
        """
        _p = os.path.join
        if self.info._config_file.find("yaml") == -1:
            self.info._config_file += ".yaml"
        folder = _p("config",_p("device","filterwheel"))
        if not os.path.exists(folder):
            os.mkdir(folder)
        path = _p(_p(_p(_p(os.getcwd(),"config"),"device"),"filterwheel"),self.info._config_file)
        if os.path.isfile(path):
            """TODO"""
        try:
            with open(path,mode="w+",encoding="utf-8") as file:
                safe_dump(self.info.get_dict(), file)
        except IOError as exception:
            log.loge(_(f"Faild to save configuration file {path} error : {exception}"))
            return self.return_message("error", _("Faild to save configuration file %(path)"),self.info.get_dict())
        log.log(_("Save configuration file successfully"))
        return self.return_message("success", _("Save configuration file successfully"),self.info.get_dict())