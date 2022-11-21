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

import gettext
_ = gettext.gettext

class Device():
    """Basic Device class.All devices should parent this class"""

    def __init__(self) -> None:
        """Constructor | 构造函数"""

    def __del__(self) -> None:
        """Destructor | 析构函数"""

    def connect(self,params : dict) -> dict:
        """Connect to the device and return in dict format | 连接设备并且以字典的形式返回结果"""
        log.loge(_("The parent function should not be called"))
        return self.return_message("error","The parent function should not be called")

    def disconnect(self,params : dict) -> dict:
        """Disconnect from the device and return in dict format | 与设备断开连接并以字典的形式返回结果"""
        log.loge(_("The parent function should not be called"))
        return self.return_message("error","The parent function should not be called")

    def return_message(self,status : str, message : str ,params = {}) -> dict:
        """
            Return the message in dict format | 以字典的形式返回结果
            :param status:
            :param message:
            :param params:
            :return: {
                "status": str,
                "message": str,
                "params": dict
            }
        """
        return {
            "status" : status,
            "message" : message,
            "params" : params
        }

    def update_config(self) -> dict:
        """Update the configuration | 更新配置，通常在初次连接设备时执行"""
        log.loge(_("The parent function should not be called"))
        return self.return_message("error","The parent function should not be called")

    def set_config(self,params : dict) -> dict:
        """set the configuration and return the result"""
        log.loge(_("The parent function should not be called"))
        return self.return_message("error","The parent function should not be called")

    def load_config(self,params : dict) -> dict:
        """Load the configuration | 加载配置，通常在初次连接设备时执行"""
        log.loge(_("The parent function should not be called"))
        return self.return_message("error","The parent function should not be called")

    def save_config(self) -> dict:
        """Save the configuration | 保存配置，通常在结束程序时运行"""
        log.loge(_("The parent function should not be called"))
        return self.return_message("error","The parent function should not be called")

    def refresh_info(self) -> dict:
        """Refresh the information and return in dict format | 以字典的形式返回返回设置信息"""
        log.loge(_("The parent function should not be called"))
        return self.return_message("error","The parent function should not be called")