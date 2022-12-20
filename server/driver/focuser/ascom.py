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

from time import sleep
from server.basic.focuser import BasicFocuserAPI,BasicFocuserInfo
from libs.alpyca.focuser import Focuser
from libs.alpyca.exceptions import (DriverException,
                                        NotConnectedException,
                                        NotImplementedException,
                                        InvalidValueException,
                                        InvalidOperationException)

from utils.lightlog import lightlog
log = lightlog(__name__)

import gettext
_ = gettext.gettext

from json import dumps
from os import mkdir, path

class AscomFocuserAPI(BasicFocuserAPI):
    """
        ASCOM Focuser API via alpyca
    """

    def __init__(self) -> None:
        self.info = BasicFocuserInfo()
        self.device = None
        self.info._is_connected = False

    def __del__(self) -> None:
        if self.info._is_moving:
            self.abort_movement()
        if self.info._is_connected:
            self.disconnect()
    
    def connect(self, params: dict) -> dict:
        """
            Connect to ASCOM focuser | 连接ASCOM电调
            Args: {
                "host": "127.0.0.1",
                "port": 8888,
                "device_number" : int # default is 0
            }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : {
                    "info" : BasicFocuserInfo object
                }
            }
        """
        if self.info._is_connected:
            log.logw(_("Focuser is connected, please do not execute connect command again"))
            return log.return_warning(_("Focuser is connected"),{})
        if self.device is not None:
            log.logw(_("Each server can only connect to one device at a time"))
            return log.return_warning(_("Each server can only connect to one device at a time"),{})
        host = params.get('host')
        port = params.get('port')
        device_number = params.get('device_number')
        if host is None or port is None or device_number is None:
            log.logw(_("Host and port must be specified"))
            return log.return_warning(_("Host or port or device_number is None"),{})
        try:
            self.device = Focuser(host + ":" + str(port), device_number)
            self.device.Connected = True
        except DriverException as e:
            log.loge(_(f"Faild to connect to device on {host}:{port}"))
            return log.return_error(_(f"Failed to connect to device on {host}:{port}"))
        except ConnectionError as e:
            log.loge(_(f"Network error while connecting to focuser , error : {e}"))
            return log.return_error(_("Network error while connecting to focuser"),{"error" : e})
        log.log(_("Connected to device successfully"))
        res = self.get_configration()
        if res.get('status') != 0:
            return log.return_error(_(f"Failed tp load focuser configuration"),{})
        self.info._is_connected = True
        self.info._type = "ascom"
        return log.return_success(_("Connect to focuser successfully"),{"info":res.get("info")})

    def disconnect(self) -> dict:
        """
            Disconnect from ASCOM focuser | 断链
            Args: None
            Returns: {
                "status" : int,
                "message" : str,
                "params" : None
            }
            NOTE : This function must be called before destory all server
        """
        if not self.info._is_connected or self.device is None:
            log.logw(_("Focuser is not connected, please do not execute disconnect command"))
            return log.return_warning(_("Focuser is not connected"),{})
        try:
            self.device.Connected = False
        except DriverException as e:
            log.loge(_(f"Faild to disconnect from device , error : {e}"))
            return log.return_error(_(f"Failed to disconnect from device"),{"error" : e})
        except ConnectionError as e:
            log.loge(_(f"Network error while disconnecting from focuser, error : {e}"))
            return log.return_error(_(f"Network error while disconnecting from focuser"),{"error" : e})
        self.device = None
        self.info._is_connected = False
        log.log(_("Disconnected from focuser successfully"))
        return log.return_success(_("Disconnect from focuser successfully"),{"params":None})

    def reconnect(self) -> dict:
        """
            Reconnect to ASCOM focuser | 重连
            Args: None
            Returns: {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """
        if self.device is None or not self.info._is_connected:
            log.logw(_("Focuser is not connected, please do not execute reconnect command"))
            return log.return_warning(_("Focuser is not connected"),{}) 
        try:
            self.device.Connected = False
            sleep(1)
            self.device.Connected = True
        except DriverException as e:
            log.loge(_(f"Faild to reconnect to device, error : {e}"))
            return log.return_error(_(f"Failed to reconnect to device"),{"error" : e})
        except ConnectionError as e:
            log.loge(_(f"Network error while reconnecting to focuser, error : {e}"))
            return log.return_error(_(f"Network error while reconnecting to focuser"),{"error" : e})
        log.log(_("Reconnect successfully"))
        self.info._is_connected = True
        return log.return_success(_("Reconnect successfully"),{})

    def scanning(self) -> dict:
        """
            Scan the focuser | 扫描电调
            Args: None
            Returns: {
                "status" : int,
                "message" : str,
                "params" : {
                    "focuser" : list
                }
            }
        """

    def polling(self) -> dict:
        """
            Polling for ASCOM focuser
            Args: None
            Returns: {
                "status" : int,
                "message" : str,
                "params" : {
                    "info" : BasicFocuserInfo object
                }
            }
        """
        if self.device is None or not self.info._is_connected:
            log.logw(_("Focuser is not connected, please do not execute polling command"))
            return log.return_warning(_("Focuser is not connected"),{})
        res = self.info.get_dict()
        log.logd(_(f"New focuser info : {res}"))
        return log.return_success(_("Focuser's information is refreshed"),{"info":res})

    def get_configration(self) -> dict:
        """
            Get focuser infomation | 获取电调信息
            Args: None
            Returns: {
                "status" : int,
                "message" : str,
                "params" : {
                    "info" : BasicFocuserInfo object
                }
            }
        """
        try:
            self.info._name = self.device.Name
            log.logd(_(f"Focuser name : {self.info._name}"))
            self.info._id = self.device._client_id
            log.logd(_(f"Focuser ID : {self.info._id}"))
            self.info._description = self.device.Description
            log.logd(_(f"Focuser description : {self.info._description}"))
            self.info._ipaddress = self.device.address
            log.logd(_(f"Focuser IP address : {self.info._ipaddress}"))
            self.info._api_version = self.device.api_version
            log.logd(_(f"Focuser API version : {self.info._api_version}"))

            self.info._can_temperature = self.device.TempCompAvailable
            log.logd(_(f"Can focuser get temperature: {self.info._can_temperature}"))
            if self.info._can_temperature:
                try:
                    self.info._temperature = self.device.Temperature
                    log.logd(_(f"Focuser current temperature : {self.info._temperature}°C"))
                except NotImplementedException as e:
                    log.loge(_(f"Failed to get current temperature , error: {e}"))
            else:
                self.info._temperature = -256
            
        except NotConnectedException as e:
            log.loge(_("Remote device is not connected"))
            return log.return_error(_("Remote device is not connected",{}))
        except DriverException as e:
            pass
        except ConnectionError as e:
            log.loge(_(f"Network error while get focuser configuration , error : {e}"))
            return log.return_error(_("Network error while get focuser configuration"),{"error":e})
        log.log(_("Get focuser configuration successfully"))
        return log.return_success(_("Get focuser configuration successfully"),{"info" : self.info.get_dict()})

    def set_configration(self, params: dict) -> dict:
        return super().set_configration(params)

    def load_configration(self) -> dict:
        return super().load_configration()

    def save_configration(self) -> dict:
        """
            Save configration of focuser
            Args : None
            Return : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """
        _p = path.join
        _path = _p("config",_p("focuser",self.info._name+".json"))
        if not path.exists("config"):
            mkdir("config")
        if not path.exists(_p("config","focuser")):
            mkdir(_p("config","focuser"))
        self.info._configration = _path
        with open(_path,mode="w+",encoding="utf-8") as file:
            file.write(dumps(self.info.get_dict(),indent=4,ensure_ascii=False))
        log.log(_("Save focuser information successfully"))
        return log.return_success(_("Save focuser information successfully"),{})