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

class BasicDeviceAPI(object):
    """
        Basic Device API 
    """

    def __init__(self) -> None:
        """
            Constructor | 构造函数\n
            Args:
                None
            Raises:
                None
            Usage:
                Initialize info container and device
        """

    def __del__(self) -> None:
        """
            Destructor | 析构函数\n
            Args:
                None
            Raises:
                None
            Usage:
                Check if device is still running , and cancel all missions
        """

    def connect(self , params : dict) -> dict:
        """
            Connect to device | 连接设备\n
            Args:
                params : {
                    "name" : str # name of device
                    "type" : str # type of device
                    "ip" : str # ip of device , ASCOM and INDI only
                    "port" : int # port of device , ASCOM and INDI only
                }
            Usage:
                Connect to device
            Returns:{
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    def disconnect(self) -> dict:
        """
            Disconnect from device | 与设备断开连接\n
            Args:
                None
            Usage:
                Disconnect from device
            Returns: {
                "status" : int,
                "message" : str,
                "params" : None
            }
            NOTE : This function must be called when destory self !
        """

    def reconnect(self) -> dict:
        """
            Reconnect to device | 重新连接设备\n
            Args:
                None
            Usage:
                Reconnect to device
            Returns: {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    def scanning(self) -> dict:
        """
            Scanning of device | 扫描已连接设备\n
            Args:
                None
            Usage:
                Scanning of device
            Returns: {
                "status" : int,
                "message" : str,
                "params" : {
                    "device" : list # list of devices
                }
            }
            NOTE : This function is suggested to be used when trying to connect devices
        """

    def polling(self) -> dict:
        """
            Polling of device | 获取设备最新信息\n
            Args:
                None
            Usage:
                Polling of device newest infomation
            Returns: {
                "status" : int,
                "message" : str,
                "params" : {
                    "info" : Device Info object
                }
            }
            NOTE : This function's old name is update_config()
        """

    def get_configration(self) -> dict:
        """
            Get configration of device | 获取设备配置\n
            Args:
                None
            Usage:
                Get configration of device
            Returns: {
                "status" : int,
                "message" : str,
                "params" : {
                    "info" : Device Info object
                }
            }
            NOTE : This function usually is called when initial the device
        """

    def set_configration(self) -> dict:
        """
            Set configration of device | 修改设备配置\n
            Args:
                None
            Usage:
                Set configration of device
            Returns: {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    def load_configration(self) -> dict:
        """
            Load configration of device | 读取设备配置\n
            Args:
                None
            Usage:
                Load configration of device
            Returns: {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    def save_configration(self) -> dict:
        """
            Save configration of device | 保存设备配置\n
            Args:
                None
            Usage:
                Save configration of device
            Returns: {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """