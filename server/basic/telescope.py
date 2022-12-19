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

from .device import BasicDeviceAPI

class BasicTelescopeAPI(BasicDeviceAPI):
    """
        Basic Telescope API
    """

    def __init__(self) -> None:
        return super().__init__()
    
    def __del__(self) -> None:
        return super().__del__()

    # #################################################################
    #
    # Telescope Basic API
    #
    # #################################################################

    def goto(self,params : dict) -> dict:
        """
            Go to a specific place\n
            Args:   
                NOTE : If ra and dec are given , please do not provide az and alt
                params : {
                    "j2000": boolean # True if the coordinates given are in the format of J2000
                    "ra" : str # xx:xx:xx
                    "dec" : str # +-xx:xx:xx
                    "az" : str # xx:xx:xx
                    "alt" : str # xx:xx:xx
                }
            Returns:
                {
                    "status" : int
                    "message" : str
                    "params" : {
                        "ra" : str
                        "dec" : str
                    }
                }
        """

    def abort_goto(self) -> dict:
        """
            Abort goto process\n
            Returns:
                {
                    "status" : int
                    "message" : str
                    "params" : {
                        "ra" : str
                        "dec" : str
                    }
                }
            NOTE : The RA and DEC returned are current position telescope target at
        """

    def get_goto_status(self) -> dict:
        """
            Get goto status\n
            Returns:
                {
                    "status" : int
                    "message" : str
                    "params" : {
                        "is_moving" : boolean
                        "ra" : str
                        "dec" : str
                    }
                }
            NOTE : This function is used to check whether telescope is slewing and return current position
        """

    def get_goto_result(self) -> dict:
        """
            Get goto result\n
            Returns:
                {
                    "status" : int
                    "message" : str
                    "params" : {
                        "ra" : str
                        "dec" : str
                    }
                }
            NOTE : This function is suggested to be called after goto process is finished
        """

    def sync(self , params : dict) -> dict:
        """
            Sync telescope\n
            Args:   
                NOTE : If ra and dec are given, please do not provide az and alt
                params : {
                    "j2000": boolean # True if the coordinates given are in the format of J2000
                    "ra" : str # xx:xx:xx
                    "dec" : str # +-xx:xx:xx
                    "az" : str # xx:xx:xx
                    "alt" : str # xx:xx:xx
                }
            Returns:
                {
                    "status" : int
                    "message" : str
                    "params" : {
                        "ra" : str
                        "dec" : str
                        "az" : str
                        "alt" : str
                    }
                }
            NOTE : This function may need telescope support
        """

    def abort_sync(self) -> dict:
        """
            Abort sync process\n
            Returns:
                {
                    "status" : int
                    "message" : str
                    "params" : {
                        "ra" : str
                        "dec" : str
                    }
                }
            NOTE : The RA and DEC returned are current position telescope target at
        """
    
    def get_sync_status(self) -> dict:
        """
            Get sync status\n
            Returns:
                {
                    "status" : int
                    "message" : str
                    "params" : {
                        "is_moving" : boolean
                        "ra" : str
                        "dec" : str
                    }
                }
        """

    def get_sync_result(self) -> dict:
        """
            Get sync result\n
            Returns:
                {
                    "status" : int
                    "message" : str
                    "params" : {
                        "ra" : str
                        "dec" : str
                        "az" : str
                        "alt" : str
                    }
                }
            NOTE : This function is suggested to be called after sync process is finished
        """

    # #################################################################
    #
    # Telescope Properties
    #
    # #################################################################

    @property
    def telescope_ra(self) -> dict:
        """
            Get telescope RA\n
            Returns:
                {
                    "status" : int
                    "message" : str
                    "params" : {
                        "ra" : str
                    }
                }
            NOTE : The RA returned are current position telescope target at
        """

    @property
    def telescope_dec(self) -> dict:
        """
            Get telescope DEC\n
            Returns:
                {
                    "status" : int
                    "message" : str
                    "params" : {
                        "dec" : str
                    }
                }
            NOTE : The DEC returned are current position telescope target at
        """

    @property
    def telescope_az(self) -> dict:
        """
            Get the AZ of telescope\n
            Returns:
                {
                    "status" : int
                    "message" : str
                    "params" : {
                        "az" : str
                    }
                }
            NOTE : The AZ returned are current position telescope target at
        """

    @property
    def telescope_alt(self) -> dict:
        """
            Get current position 
            Returns:
                {
                    "status" : int
                    "message" : str
                    "params" : {
                        "alt" : str
                    }
                }
            NOTE : The ALT returned are current position telescope target at
        """

    # #################################################################
    #
    # Telescope Status
    #
    # #################################################################

    @property
    def is_connected(self) -> dict:
        """
            Check if telescope is connected
            Returns:
                {
                    "status" : int
                    "message" : str
                    "params" : {
                        "is_connected" : boolean
                    }
                }
        """

    @property
    def is_slewing(self) -> dict:
        """
            Check if the telescope is slewing
            Returns:
                {
                    "status" : int
                    "message" : str
                    "params" : {
                        "is_slewing" : boolean
                    }
                }
        """