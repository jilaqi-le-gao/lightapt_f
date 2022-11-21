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

from driver.basicdevice import Device
from utils.lightlog import lightlog

log = lightlog(__name__)

import gettext
_ = gettext.gettext

__api__ = "Focuser Basic API"
__api_version__ = "1.0.0"
__copyright__ = "Max Qian"
__license__ = "GPL3"

# #################################################################
#
# Focuser Info Class
#
# #################################################################

class FocuserInfo(object):
    """Focuser Info class for containing focuser information"""

    """Basic Info"""
    _address = None # For ASCOM & INDI
    _name = None
    _api_version : str
    _description : str
    _id : int
    _timeout = 5
    _config_file : str

    """Property Info"""
    _current_position : int
    _max_steps : int
    _max_steps_ : int
    _step_size : int
    _temperature : float

    """Status Info"""
    _is_connected = False
    _is_moving = False
    _is_operating = False

    """Availability Info"""
    _can_temperature = False

    def get_dict(self) -> dict:
        """Return focuser information in a dictionary"""
        r = {
            "address": self._address,
            "api_version" : self._api_version,
            "description": self._description,
            "id": self._id,
            "timeout" : self._timeout,
            "ability" : {
                "can_temperature" : self._can_temperature
            },
            "property" : {
                "max_steps" : self._max_steps,
                "max_steps_single" : self._max_steps_,
                "step_size" : self._step_size,
                "temperature" : self._temperature
            },
            "status" : {
                "is_connected" : self._is_connected,
                "is_moving" : self._is_moving,
            }
        }
        return r

        
# #################################################################
# 
# Base class for focuser control
#
# #################################################################

class BasicFocuser(Device):
    """Focuser control class based on Device class"""

    def __init__(self) -> None:
        """Initial Class"""

    def __del__(self) -> None:
        """Delete Class"""

    def connect(self,params : dict) -> dict:
        """
            Connect to Focuser and finish all the initialization process
            连接电调并且完成所有的初始化
            @ params : {
                "count" : number of focuser # Default is 1
                "name" : string # To check if the focuser is you need
            }
        """
        return super().connect(params)     

    def disconnect(self,params : dict) -> dict:
        """
            Disconnect from focuser and after execute this function we will lose connection with focuser.And should realize all the resources
            与电调断开连接，完成此步后就结束了任务，需要释放所有资源
        """
        return super().disconnect()

    def update_config(self) -> dict:
        """
            Update the configuration of the focuser . execute this function after "connect"
            更新电调配置，通常在连接成功后执行
        """
        return super().update_config()

    def set_config(self,params : dict) -> dict:
        """
            Set the configuration of the current Focuser
            设置电调参数
            @ params : {

            }
        """
        return super().set_config(params)

    def load_config(self, params: dict) -> dict:
        """
            Load the configuration of the current Focuser
            加载电调配置
        """
        return super().load_config(params)

    def save_config(self) -> dict:
        """
            Save the configuration of the focuser . execute this function after "disconnect"
            保存电调配置，通常在断开连接后执行
        """
        return super().save_config()

    def refresh_info(self) -> dict:
        """
            Refresh the Focuser Information and return it to the function which called this function
            更新电调信息并且返回给调用此函数的函数
        """
        return super().refresh_info()

    def move(self,params : dict) -> dict:
        """
            Move the Focuser position 
            移动电调位置
            @ params : {
                "direction": "front","back"
                "step" : int # step number
                "speed" : int # speed ? Will this be supported
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def moveto(self,params : dict) -> dict:
        """
            Move to the current you set position
            @ params : {
                "position" : int # position
                "speed" : int # speed ? Will this be supported
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def abort(self) -> dict:
        """
            Abort the current movement

        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def get_position(self) -> dict:
        """
            Get the current position of the current Focuser
            获取电调当前位置
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def get_temperature(self) -> dict:
        """
            Get the current temperature of the current Focuser
            获取电调当前温度
            Note: This function needs focuser support
            提示： 这个功能需要电调支持
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))