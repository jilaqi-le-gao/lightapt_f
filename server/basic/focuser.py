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

from server.basic.device import BasicDeviceAPI

class BasicFocuserInfo(object):
    """
        Focuser Info class for containing focuser information
    """

    _type = "" # type of the camera , must be given
    _name : str # name of the camera
    _id : int # id of the camera
    _description : str
    _timeout = 5
    _configration = "" # path to the configuration file

    _ipaddress : str # IP address only ASCOM and INDI
    _api_version : str # API version only ASCOM and INDI

    _current_position : int
    _step_size : int
    _temperature : float

    _max_steps : int
    
    _is_connected = False
    _is_moving = False
    _is_compensation = False

    _can_temperature = False

    def get_dict(self) -> dict:
        """
            Return focuser information in a dictionary
            Args: None
            Returns: dict
        """
        return {
            "type": self._type,
            "name": self._name,
            "id": self._id,
            "description": self._description,
            "timeout": self._timeout,
            "configration": self._configration,
            "current" : {
                "position" : self._current_position,
                "step_size" : self._step_size,
                "temperature" : self._temperature
            },
            "abilitiy" : {
                "can_temperature" : self._can_temperature
            },
            "status" : {
                "is_connected" : self._is_connected,
                "is_moving" : self._is_moving
            },
            "properties" : {
                "max_steps" : self._max_steps,
            },
            "network" : {
                "ipaddress" : self._ipaddress,
                "api_version" : self._api_version,
            }
        }

class BasicFocuserAPI(BasicDeviceAPI):
    """
        Basic Focuser API
    """

    def __init__(self) -> None:
        super().__init__()

    def __del__(self) -> None:
        super().__del__()

    # #################################################################
    #
    # Focuser Basic API
    #
    # #################################################################

    def move_step(self, params : dict) -> dict:
        """
            Focuser move given step | 电调移动指定步数
            Args :
                params : {
                    "step" : int
                }
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    def move_to(self , params : dict) -> dict:
        """
            Move to target position | 移动至指定位置
            Args :
                params : {
                    "position" : int
                }
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    def abort_movement(self) -> dict:
        """
            Abort movement | 停止
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    def get_temperature(self) -> dict:
        """
            Get focuser temperature | 获取电调温度
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "temperature" : float
                }
            }
            NOTE : This function needs focuser support
        """

    def get_movement_status(self) -> dict:
        """
            Get focuser movement status
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : int
                }
            }
        """