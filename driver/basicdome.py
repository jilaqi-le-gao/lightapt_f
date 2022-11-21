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

__api__ = "Dome Basic API"
__api_version__ = "1.0.0"
__copyright__ = "Max Qian"
__license__ = "GPL3"

# #################################################################
#
# Dome Info Class
#
# #################################################################

class DomeInfo(object):
    """Dome Info class for containing Dome information"""

    """Basic Info"""
    _address = None # For ASCOM & INDI
    _name = None
    _api_version : str
    _description : str
    _id : int
    _timeout = 5
    _config_file : str

    """Property Info"""
    _az : float
    _alt : float

    """Status Info"""
    _is_connected = False
    _is_operating = False
    _is_opened : str
    _is_slewing = False
    _is_parked = False
    _is_home = False
    _is_slaved = False

    """Availability Info"""
    _can_park = False
    _can_home = False
    _can_slave = False
    _can_set_az = False
    _can_set_alt = False
    _can_set_shutter = False
    _can_set_park = False
    _can_az_sync = False

    def get_dict(self) -> dict:
        """Return Dome information in a dictionary"""
        r = {
            "address": self._address,
            "api_version" : self._api_version,
            "description": self._description,
            "id": self._id,
            "timeout" : self._timeout,
            "ability" : {
                "can_park" : self._can_park,
                "can_home" : self._can_home,
                "can_slave " : self._can_slave,
                "can_set_az" : self._can_set_az,
                "can_set_alt" : self._can_set_alt,
                "can_set_shutter" : self._can_set_shutter,
                "can_set_park" : self._can_set_park,
                "can_az_sync" : self._can_az_sync
            },
            "property" : {
                "az" : self._az,
                "alt" : self._alt
            },
            "status" : {
                "is_parked" : self._is_parked,
                "is_home" : self._is_home,
                "is_slewing" : self._is_slewing,
                "is_opened" : self._is_opened,
                "is_slaved" : self._is_slaved,
            }
        }
        return r

# #################################################################
# 
# Base class for Dome control
#
# #################################################################

class BasicDome(Device):
    """Dome control class based on Device class"""

    def __init__(self) -> None:
        """Initial Class"""

    def __del__(self) -> None:
        """Delete Class"""

    def connect(self,params : dict) -> dict:
        """
            Connect to Dome and finish all the initialization process
            连接穹顶并且完成所有的初始化
            @ params : {
                "count" : number of Dome # Default is 1
                "name" : string # To check if the Dome is you need
            }
        """
        return super().connect(params)     

    def disconnect(self,params : dict) -> dict:
        """
            Disconnect from Dome and after execute this function we will lose connection with Dome.And should realize all the resources
            与穹顶断开连接，完成此步后就结束了任务，需要释放所有资源
        """
        return super().disconnect()

    def update_config(self) -> dict:
        """
            Update the configuration of the Dome . execute this function after "connect"
            更新穹顶配置，通常在连接成功后执行
        """
        return super().update_config()

    def set_config(self,params : dict) -> dict:
        """
            Set the configuration of the current Dome
            设置穹顶参数
            @ params : {

            }
        """
        return super().set_config(params)

    def load_config(self, params: dict) -> dict:
        """
            Load the configuration of the current Dome
            加载穹顶配置
        """
        return super().load_config(params)

    def save_config(self) -> dict:
        """
            Save the configuration of the Dome . execute this function after "disconnect"
            保存穹顶配置，通常在断开连接后执行
        """
        return super().save_config()

    def refresh_info(self) -> dict:
        """
            Refresh the Dome Information and return it to the function which called this function
            更新穹顶信息并且返回给调用此函数的函数
        """
        return super().refresh_info()
