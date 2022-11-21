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
the Free Software Foundation, Inctypes., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301, USA.

"""

from utils.lightlog import lightlog
from driver.basictelescope import (BasicTelescope,TelescopeInfo)
from libs.alpyca.telescope import Telescope
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

class telescope(BasicTelescope):
    """ASCOM telescope class (via ASCOM Remote)"""

    def __init__(self) -> None:
        """Construct"""
        self.info = TelescopeInfo()
        self.device = None
        log.log(_("Initialize ASCOM telescope object successfully"))

    def __del__(self) -> None:
        """Delete ASCOM device object"""
        if self.info._is_connected:
            if self.disconnect({}).get("status") != "success":
                log.loge(_("Failed to disconnect from ASCOM Remote telescope"))
                return
        self.device = None
        log.log(_("Delete ASCOM Remote telescope object successfully"))

    def connect(self, params: dict) -> dict:
        """
            Connect to ASCOM telescope | 连接ASCOM赤道仪
            Args:
                params: {
                    "host" : str , default host is "127.0.0.1"
                    "port" : int # default port is 11111
                    "device_number" : int # default is 0
                }
            Returns:
                {
                    "status" : " "success","error","warning","debug"
                    "message" : "ASCOM telescope is connected" # success
                                "Faild to connect to ASCOM telescope" # error
                                "ASCOM telescope is connected with warning" # warning
                                "Attempt to connect to ASCOM telescope in debug mode" # debug
                    "params" : {
                        "name" : str # 
                        "info" : TelescopeInfo object
                    }
                }
        """
        # Check if the parameters are valid | 检查选项是否合法
        if not isinstance(params,dict):
            log.loge(_("Invalid parameters"))
            return self.return_message("error",_("Invalid parameters"),{})
        # Load information from the parameters | 读取参数
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
            self.device = Telescope(ip_address,device_number)
            self.device.Connected = True
            self.info._is_connected = True
        except DriverException as exception:
            log.loge(_(f"Failed to connect to telescope , error: {exception}"))
            return self.return_message("error",_("Failed to connect to Telescope"),{"error": exception})
        except ConnectionError as exception:
            log.loge(_(f"Remote connection error: {exception}"))
            return self.return_message("error",_("Remote connection error"),{"error": exception})
        log.log(_("Connected to telescope successfully"))
        # Update Telescope Infomation | 更新赤道仪信息
        res = self.update_config()
        if res.get("status") != "success":
            return res
        r = {
            "name" : self.info._name,
            "info" : res.get("params")
        }
        return self.return_message("success",_("Connected to Telescope successfully"),r)

    def disconnect(self, params: dict) -> dict:
        """
            Disconnect from ASCOM telescope
            Args:
                params: {
                    "name" : str
                }
            Returns:
                {
                    "status" : " "success","error","warning","debug"
                    "message" : "Disconnect from ASCOM telescope successfully" # success
                                "Faild to disconnect from ASCOM telescope" # error
                                "ASCOM telescope is disconnected with warning" # warning
                                "Attempting to disconnect from ASCOM telescope in debug mode" # debug
                    "params" : {
                        "error" : error message # usually exception
                    }
                }
            Note : Must disconnect from telescope when destory self !
        """
        log.log(_("Try to disconnect from ASCOM telescope"))
        name = params.get("name")
        try:
            self.device.Connected = False
            self.info._is_connected = False
        except DriverException as e:
            log.loge(_("Failed to disconnect from telescope , error : %s"),e)
            return self.return_message("error",_("Failed to disconnect from ASCOm telescope"),{"error" : exception})
        except ConnectionError as exception:
            log.loge(_(f"Remote connection error: {exception}"))
            return self.return_message("error",_("Remote connection error"),{"error" : exception})
        log.log(_("Disconnect from ASCOM telescope successfully"))
        return self.return_message("success",_("Disconnect from ASCOM telescope successfully"),{})
    
    def update_config(self) -> dict:
        """
            Update configuration of ASCOM telescope
            Returns:
                {
                    "status" : "success","error","warning","debug"
                    "message" : "Update configuration successfully" # success
                                "Faild to update configuration" # error
                                "ASCOM configuration is updated with warning" # warning
                                "Attempting to update configuration in debug mode" # debug
                    "params" : {
                        "info" : TelescopeInfo object (use get_dict())
                        "error" : error message # usually exception
                    }
                }
            Note : This function is usually run when initialize the telescope
        """
        log.log(_("Update ASCOM telescope configuration"))
        try:
            """Get basic information | 获取基础信息"""
            self.info._address = self.device.address
            self.info._name = self.device.Name
            self.info._api_version = self.device.api_version
            self.info._id = self.device._client_id
            self.info._coordinates_type = self.device.EquatorialSystem.value
            self.info._description = self.device.Description
            """Get ability information | 获取能力信息 (即是否能够执行某些功能)"""
            self.info._can_slewing = self.device.CanSlew
            self.info._can_park = self.device.CanPark
            self.info._can_unpark = self.device.CanUnpark
            self.info._can_home = self.device.CanFindHome
            self.info._can_tracking = self.device.CanSetTracking
            self.info._can_guiding = self.device.CanPulseGuide
            self.info._can_set_park = self.device.CanSetPark
            self.info._can_set_home = self.device.CanFindHome
            self.info._can_set_ra_rate = self.device.CanSetRightAscensionRate
            self.info._can_set_dec_rate = self.device.CanSetDeclinationRate
            """Get property infomation | 获取配置信息"""
            self.info._lon = self.device.SiteLongitude
            self.info._lat = self.device.SiteLatitude
            self.info._tracking_ra_rate = self.device.RightAscensionRate
            self.info._tracking_dec_rate = self.device.DeclinationRate
            self.info._guiding_ra_rate = self.device.GuideRateRightAscension
            self.info._guiding_dec_rate = self.device.GuideRateDeclination
            self.info._slewing_ra_rate = 1.0
            self.info._slewing_dec_rate = 1.0
            """Get current telescope information | 获取赤道仪当前信息"""
            self.info._ra = self.device.RightAscension
            self.info._dec = self.device.Declination
            self.info._az = self.device.Azimuth
            self.info._alt = self.device.Altitude
            coord = self.calc_coordinates({"type": "h","RA" : self.info._ra,"DEC": self.info._dec}).get("params")
            self.info._convert_ra = coord.get("RA")
            self.info._convert_dec = coord.get("DEC")
            coord = self.calc_coordinates({"type": "h","RA" : self.info._az,"DEC": self.info._alt}).get("params")
            self.info._convert_az = coord.get("RA")
            self.info._convert_alt = coord.get("DEC")
            """Get current status of the telescope | 获取赤道仪当前状态"""
            self.info._is_parked = self.device.AtPark
            self.info._is_home = self.device.AtHome
            self.info._is_tracking = self.device.Tracking
            self.info._is_slewing = self.device.Slewing
            self.info._is_guiding = self.device.IsPulseGuiding
            """Set configuration file name | 设置配置文件名称默认为设备名称"""
            self.info._config_file = self.device.Name
        except NotConnectedException as exception:
            log.loge(_("No telescope connected , please connect to telescope before run update_config()"))
            return self.return_message("error", _("No telescope connected"),{"error" : exception})
        except DriverException as exception:
            log.loge(_("Telescope driver error , when run update_config()"))
            return self.return_message("error", _("Telescope driver error"),{"error" : exception})
        except ConnectionError as exception:
            log.loge(_("Remote server connection error, when run update_config()"))
            return self.return_message("error",_("Remote connection error"),{"error" : exception})
        
        log.log(_("Update telescope configuration successfully"))
        return self.return_message("success", _("Update telescope configuration successfully"),self.info.get_dict())

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
        try:
            if self.info._config_file.find("yaml") == -1:
                self.info._config_file += ".yaml"
            if not os.path.exists("config"):
                os.mkdir("config")
            if not os.path.exists(_p("config","device")):
                os.mkdir(_p("config","device"))
            folder = _p("config",_p("device","telescope"))
            if not os.path.exists(folder):
                os.mkdir(folder)
        except FileNotFoundError as exception:
            """FileNotFoundError"""
        path = _p(_p(_p(_p(os.getcwd(),"config"),"device"),"telescope"),self.info._config_file)
        try:
            with open(path,mode="w+",encoding="utf-8") as file:
                safe_dump(self.info.get_dict(), file)
        except IOError as exception:
            log.loge(_(f"Faild to save configuration file {path} error : {exception}"))
            return self.return_message("error", _("Faild to save configuration file %(path)"),self.info.get_dict())
        log.log(_("Save configuration file successfully"))
        return self.return_message("success", _("Save configuration file successfully"),self.info.get_dict())

    def refresh_info(self) -> dict:
        """
            Refresh telescope information | 刷新赤道仪信息
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : {
                    "error" : exception
                    "info" : self.info
                }
            }
        """
        r = {
            "status" : "success",
            "message" : "Refresh information",
            "params" : {
                "info" : self.info.get_dict()
            }
        }
        return r
    
    # ###########################################################
    # Goto Functions
    # ###########################################################

    def goto(self, params: dict) -> dict:
        """
            Goto the current coordinates
            Args:
                params : {
                    "mode" : str # "p"(ra,dec) or "h"(az,alt)
                    "crood_type" : str # "J2000" or "JNow"
                    "input_type" : str # "h" or "f" default is "h"
                    "ra" : str | float 
                    "dec" : str | float 
                    "az" : str | float
                    "alt" : str | float
                }
            Return:
                {
                    "status" : str # "success","error","warning","debug"
                    "message" : "Goto the specified coordinates successfully" # success
                                "Faild to goto the specified coordinates" # error
                                "Goto the specified coordinates with warning" # warning
                    "params" : {
                        "error" : exception
                        "info" : {
                            "ra" : ra
                            "dec" : dec
                            "az" : az
                            "alt" : alt
                        }
                    }

                }
        """
        while self.info._is_operating:
            sleep(1)
        self.info._is_operating = True
        # Check if the telescope is available to goto | 检查赤道仪是否能否Goto
        if not self.info._can_tracking:
            log.loge(_("Telescope had no tracking mode and was not available to goto"))
            return self.return_message("error", _("Telescope had no tracking mode"),{"advice" : "Change a telescope"})
        if not self.info._can_slewing:
            log.loge(_("Telescope had no slewing mode and was not available to goto"))
            return self.return_message("error", _("Telescope had no slewing mode"),{"advice" : "Change a telescope"})
        # Check the coordinates
        mode = params.get("mode")
        input_type = params.get("input_type")
        ra = params.get("ra")
        dec = params.get("dec")
        az = params.get("az")
        alt = params.get("alt")
        # Check if the inneed coordinates are given | 检查是否包含需要的参数
        if mode == "p" : 
            if ra is None and dec is None:
                log.loge(_("EmptyString"))
                return self.return_message("error", _("EmptyString"),{})
        elif mode == "h" :
            if az is None and alt is None:
                log.loge(_("EmptyString"))
                return self.return_message("error", _("EmptyString"),{})
        else:
            log.loge(_("Invalid mode"))
            return self.return_message("error", _("Invalid mode"),{})
        # Check if the coordinates type is correct | 检查坐标类型是否正确
        if input_type == "h" :
            if not isinstance(ra,str) or not isinstance(dec,str):
                log.loge(_("Invalid input coordinates type"))
                return self.return_message("error", _("Invalid input coordinates type"),{})
        elif input_type == "f":
            if not isinstance(ra,float) or not isinstance(dec,float):
                log.loge(_("Invalid input coordinates type"))
                return self.return_message("error", _("Invalid input coordinates type"),{})
        else:
            log.loge(_("Invalid input coordinates type"))
            return self.return_message("error", _("Invalid input coordinates type"),{})
        # Convert coordinates if necessary | 如果需要的话转化坐标
        if params.get("coord_type") == "J2000":
            self.calc_coordinates_j("JNow",ra,dec)
        # Start goto the target coordinate | 开始Goto
        log.log(_(f"Start goto [{ra},{dec}]"))
        try:
            self.device.Tracking = True
            self.info._is_slewing = True
            self.device.SlewToCoordinatesAsync(ra, dec)
            log.log(_("Waiting for telescope slewing to target coordinates"))
            while self.device.Slewing:
                sleep(1)
        except NotImplementedException as exception:
            log.loge(_(f"Telescope slew error : {exception}"))
            return self.return_message("error", _("Telescope slew error"),{"error" : exception})
        except NotConnectedException as exception:
            log.loge(_("Telescope had not connected"))
            return self.return_message("error", _("Telescope had not connected"),{"error" : exception})
        except DriverException as exception:
            log.loge(_("Telescope had an error"))
            return self.return_message("error", _("Telescope had an error"),{"error" : exception})
        except ConnectionError as exception:
            log.loge(_("Remote connection error"))
            return self.return_message("error", _("Remote server connect error"),{"error" : exception})
        finally:
            self.info._is_slewing = False
            if not self.info._is_tracking:
                self.device.Tracking = False
            self.info._is_operating = False
        log.log(_(f"Successfully goto the specified coordinates : [{ra},{dec}]"))
        r = {
            "ra" : self.device.RightAscension,
            "dec" : self.device.Declination,
            "az" : self.device.Azimuth,
            "alt" : self.device.Altitude
        }
        return self.return_message("success", _("Successfully goto the specified coordinates"),r)

    def abort_goto(self) -> dict:
        """
            Abort goto operation | 终止Goto\n
            Return:
                {
                    "status" : "success","error","warning","debug"
                    "message" : "Abort goto operation successfully" # success\n
                                "Faild to abort operation" # error\n
                                "Abort operation with warning" # warning\n
                    "params" : {}
                }
            Note : This function should be thread safe , if not maybe damage telescope
        """
        while self.info._is_operating:
            sleep(1)
        self.info._is_operating = True
        if not self.info._is_slewing:
            log.logw(_("Telescope is not slewing , please do not execute abort_goto()"))
            return self.return_message("error", _("Telescope is not slewing"),{})
        try:
            self.device.Slewing = False
        except NotConnectedException as exception:
            log.loge(_("Telescope had not connected"))
            return self.return_message("error",_("Telescope had not connected"),{"error" : exception})
        except DriverException as exception:
            log.loge(_("Telescope had an error"))
            return self.return_message("error",_("Telescope had an error"),{"error" : exception})
        finally:
            self.info._is_operating = False
        self.info._is_slewing = False
        log.log(_("Abort telescope goto operation successfully"))
        return self.return_message("success", _("Abort telescope goto operation successfully"),{})

    # #########################################################################
    # Park Functions
    # #########################################################################

    def park(self) -> dict:
        """
            Park the telescope | 望远镜归位
            Return:
                {
                    "status" : "success","error","warning","debug"
                    "message" : "Park the telescope successfully" # success
                                "Faild to park" # error
                                "Park operation with warning" # warning
                    "params" : {}
                }
            Note : After this operation , telescope could not be change at all until execute unpark()
        """
        while self.info._is_operating:
            sleep(1)
        self.info._is_operating = True
        # If telescope has no park function | 如果赤道仪无法归位，那就GG
        if not self.info._can_park:
            log.loge(_("Telescope had no park function"))
            return self.return_message("error", _("Telescope had no park function"),{}) 
        # If telescope is slewing , just wait for it | 如果赤道仪正在运动中，则等待其结束
        if self.info._is_slewing:
            log.logw(_("Telescope is still slewing , waiting for it completed"))
            while self.device.Slewing:
                sleep(1)
        # If telescope is tracking , run abort_tracking() to stop it # 如果赤道仪正在跟踪就停止
        if self.info._is_tracking:
            log.logw(_("Telescope is still tracking, waiting for it completed"))
            res = self.abort_tracking()
            if res.get("status") != "success":
                return res
            while self.device.Tracking:
                sleep(1)
        # Attempting to park the telescope | 尝试赤道仪归位
        log.log(_("Attempting to park the telescope"))
        try:
            self.device.Park(True)
        except NotImplementedException as exception:
            log.loge(_(f"Telescope park error: {exception}"))
            return self.return_message("error", _("Telescope park error"),{"error" : exception})
        except NotConnectedException as exception:
            log.loge(_(f"Telescope had not connected"))
            return self.return_message("error", _("Telescope had not connected"),{"error" : exception})
        except DriverException as exception:
            log.loge(_(f"Telescope had an error : {exception}"))
            return self.return_message("error", _("Telescope had an error"), {"error" : exception})
        except ConnectionError as exception:
            log.loge(_(f"Remote connection error: {exception}"))
            return self.return_message("error", _("Remote connection error"),{"error" : exception})
        finally:
            self.info._is_operating = False
        time = 0
        while not self.device.AtPark and time < self.info._timeout:
            sleep(1)
            time += 1
        if not self.device.AtPark and time >= self.info._timeout:
            log.loge(_("Timeout waiting for telescope park operation"))
            return self.return_message("error", _("Timeout"),{"error" : "Timeout"})
        self.info._is_parked = True
        log.log(_("Telescope parked successfully"))
        return self.return_message("success", _("Telescope parked successfully"),{})

    def unpark(self) -> dict:
        """
            Unpark the telescope | 解除望远镜归位
            Return:
                {
                    "status" : "success","error","warning","debug"
                    "message" : "Telescope unpark successfully" # success message
                                "Faild to unpark" # error 
                                "Park operation with warning" # warning
                    "params" : {
                        "error" : exception
                    }
                }
            Note : This function should be called
        """
        while self.info._is_operating:
            sleep(1)
        self.info._is_operating = True
        # If telescope has no park function | 如果赤道仪无法归位，那就GG
        if not self.info._can_unpark:
            log.loge(_("Telescope had no park function"))
            return self.return_message("error", _("Telescope had no park function"),{})
        if not self.info._is_parked:
            log.logw(_("Telescope had not parked"))
            return self.return_message("warning",_("Telescope had not parked"),{})
        try:
            self.device.Unpark()
        except NotConnectedException as exception:
            log.loge(_(f"Telescope had not connected"))
            return self.return_message("error", _("Telescope had not connected"),{"error" : exception})
        except DriverException as exception:
            log.loge(_(f"Telescope had an error : {exception}"))
            return self.return_message("error", _("Telescope had an error"), {"error" : exception})
        except ConnectionError as exception:
            log.loge(_(f"Remote connection error: {exception}"))
            return self.return_message("error", _("Remote connection error"),{"error" : exception})
        finally:
            self.info._is_operating = False

        self.info._is_parked = False
        log.log_("Telescope unparked successfully")
        return self.return_message("success", _("Telescope unparked successfully"), {})
    
    # ###########################################################
    # Home Functions
    # ###########################################################

    def home(self) -> dict:
        """
            Home the telescope | 赤道仪回家
            Return:
                {
                    "status" : "success","error","warning","debug"
                    "message" : "Telescope home successfully" # success message
                                "Faild to home" # error 
                                "Home operation with warning" # warning    
                    "params" : None
                }
            Note : This function is called when you need (awa)
        """
        while self.info._is_operating:
            sleep(1)
        # If telescope has no home function
        if not self.info._can_home:
            log.loge(_("Telescope had no home function"))
            return self.return_message("error", _("Telescope had no home function"),{})
        # If telescope had already parked
        if self.info._is_parked:
            log.logw(_("Telescope had already parked"))
            return self.return_message("warning",_("Telescope had already parked"),{})
        self.info._is_operating = True
        try:
            self.device.FindHome()
        except NotImplementedException as exception:
            log.loge(_(f"Telescope had an error : {exception}"))
            return self.return_message("error", _("Telescope had an error"),{})
        except NotConnectedException as exception:
            log.loge(_(f"Telescope had not connected"))
            return self.return_message("error", _("Telescope had not connected"),{"error" : exception})
        except DriverException as exception:
            log.loge(_(f"Telescope had an error : {exception}"))
            return self.return_message("error", _("Telescope had an error"), {"error" : exception})
        except ConnectionError as exception:
            log.loge(_(f"Remote connection error: {exception}"))
            return self.return_message("error", _("Remote connection error"),{"error" : exception})
        finally:
            self.info._is_operating = False

        self.info._is_home = True
        log.log_("Telescope home successfully")
        return self.return_message("success", _("Telescope home successfully"), {})