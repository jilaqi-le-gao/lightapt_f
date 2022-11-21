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
from driver.basicdome import (BasicDome,DomeInfo)
from libs.alpyca.dome import (Dome,ShutterState)
from libs.alpyca.exceptions import (DriverException,
                                    NotConnectedException,
                                    NotImplementedException)
log = lightlog(__name__)

import os
from requests.exceptions import ConnectionError
from yaml import (safe_load,safe_dump)
import gettext
_ = gettext.gettext

class dome(BasicDome):
    """ASCOM Dome class"""

    def __init__(self) -> None:
        """Constructor"""
        self.info = DomeInfo()
        self.device = None
        log.log(_("Initializing ascom dome object"))

    def __del__(self) -> None:
        """Destructor"""
        if self.info._is_connected:
            r = self.disconnect({})
            if r.get("status") != "success":
                log.loge(_("Failed to delete ascom dome object"))
        self.device = None
        log.log(_("Successfully deleted ascom dome object"))

    def connect(self,params : dict) -> dict:
        """
            Connect to ASCOM dome
            Args:
                params: {
                    "host" : "127.0.0.1",
                    "port" : 11111,
                    "device_number" : int # default is 0
                }
            Returns:
                {
                    "status" : " "success","error","warning","debug"
                    "message" : "ASCOM dome is connected" # success
                                "Faild to connect to ASCOM dome" # error
                                "ASCOM dome is connected with warning" # warning
                    "params" : {
                        "name" : str
                        "info" : DomeInfo object
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
            self.device = Dome(ip_address,device_number)
            self.device.Connected = True
            self.info._is_connected = True
        except DriverException as exception:
            log.loge(_(f"Failed to connect to dome , error: {exception}"))
            return self.return_message("error",_("Failed to connect to dome"),{"error": exception})
        except ConnectionError as exception:
            log.loge(_(f"Remote connection error: {exception}"))
            return self.return_message("error",_("Remote connection error"),{"error": exception})
        log.log(_("Connected to dome successfully"))
        # Update dome Infomation | 更新穹顶信息
        res = self.update_config()
        if res.get("status") != "success":
            return res
        r = {
            "name" : self.info._name,
            "info" : res.get("params")
        }
        return self.return_message("success",_("Connected to dome successfully"),r)

    def disconnect(self, params : dict) -> dict:
        """
            Disconnect from ASCOM dome
            Args:
                params: {
                    "name" : str
                }
            Returns:
                {
                    "status" : " "success","error","warning","debug"
                    "message" : "Disconnect from ASCOM dome successfully" # success
                                "Faild to disconnect from ASCOM dome" # error
                                "ASCOM dome is disconnected with warning" # warning
                    "params" : {
                        "error" : error message # usually exception
                    }
                }
            Note : Must disconnect from dome when destory self !
        """
        log.log(_("Try to disconnect from ASCOM dome"))
        name = params.get("name")
        try:
            self.device.Connected = False
            self.info._is_connected = False
        except DriverException as e:
            log.loge(_("Failed to disconnect from dome , error : %s"),e)
            return self.return_message("error",_("Failed to disconnect from ASCOm dome"),{"error" : exception})
        except ConnectionError as exception:
            log.loge(_(f"Remote connection error: {exception}"))
            return self.return_message("error",_("Remote connection error"),{"error" : exception})
        log.log(_("Disconnect from ASCOM dome successfully"))
        return self.return_message("success",_("Disconnect from ASCOM dome successfully"),{})

    def update_config(self) -> dict:
        """
            Update configuration of ASCOM dome
            Returns:
                {
                    "status" : "success","error","warning","debug"
                    "message" : "Update configuration successfully" # success
                                "Faild to update configuration" # error
                                "ASCOM configuration is updated with warning" # warning
                    "params" : {
                        "info" : DomeInfo object (use get_dict())
                        "error" : error message # usually exception
                    }
                }
            Note : This function is usually run when initialize the dome
        """
        log.log(_("Update ASCOM dome configuration"))
        try:
            """Get basic information | 获取基础信息"""
            self.info._address = self.device.address
            self.info._name = self.device.Name
            self.info._api_version = self.device.api_version
            self.info._id = self.device._client_id
            self.info._description = self.device.Description
            """Get properties information | 获取配置信息"""
            self.info._can_park = self.device.CanPark
            self.info._can_home = self.device.CanFindHome
            self.info._can_slave = self.device.CanSlave
            self.info._can_set_az = self.device.CanSetAzimuth
            self.info._can_set_alt = self.device.CanSetAltitude
            self.info._can_set_park = self.device.CanSetPark
            self.info._can_set_shutter = self.device.CanSetShutter
            self.info._can_az_sync = self.device.CanSyncAzimuth
            
            self.info._is_home = self.device.AtHome
            self.info._is_parked = self.device.AtPark
            shutter_status = {
                ShutterState.shutterOpen : "opened",
                ShutterState.shutterClosed : "closed",
                ShutterState.shutterOpening : "opening",
                ShutterState.shutterClosing : "closing",
                ShutterState.shutterError : "error"
            }
            self.info._is_opened = shutter_status[self.device.ShutterStatus]
            self.info._is_slaved = self.device.Slaved
            self.info._is_slewing = self.device.Slewing
            if self.info._is_opened == ShutterState.shutterOpen:
                self.info._az = self.device.Azimuth
                self.info._alt = self.device.Altitude
            else:
                self.info._az = 1.0
                self.info._alt = 1.0
            """Set configuration file name | 设置配置文件名称默认为设备名称"""
            self.info._config_file = self.device.Name
        except NotConnectedException as exception:
            log.loge(_("No dome connected , please connect to dome before run update_config()"))
            return self.return_message("error", _("No dome connected"),{"error" : exception})
        except DriverException as exception:
            log.loge(_("dome driver error , when run update_config()"))
            return self.return_message("error", _("dome driver error"),{"error" : exception})
        except ConnectionError as exception:
            log.loge(_("Remote server connection error, when run update_config()"))
            return self.return_message("error",_("Remote connection error"),{"error" : exception})
        
        log.log(_("Update dome configuration successfully"))
        return self.return_message("success", _("Update dome configuration successfully"),self.info.get_dict())

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
        folder = _p("config",_p("device","dome"))
        if not os.path.exists(folder):
            os.mkdir(folder)
        path = _p(_p(_p(_p(os.getcwd(),"config"),"device"),"dome"),self.info._config_file)
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