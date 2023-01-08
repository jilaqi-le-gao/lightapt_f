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

class BasicTelescopeInfo(object):
    """
        Basic Telescope Info container
    """

    _ipaddress : str # IP address only ASCOM and INDI
    _api_version : str # API version only ASCOM and INDI
    _name : str # name of the camera
    _id : int # id of the camera
    _description : str
    _configration = "" # path to the configuration file

    timeout = 30

    ra = ""
    dec = ""
    az = ""
    alt = ""
    # If the GPS is enabled
    lon = ""
    lat = ""

    slewing_rate : int
    track_mode : int
    track_ra_rate : float
    track_dec_rate : float

    _can_goto = False
    _can_ahort_goto = False
    _can_sync = False
    _can_track = False
    _can_park = False
    _can_home = False
    _can_set_track_rate = False
    _can_set_track_mode = False
    _can_track_satellite = False
    _can_get_location = False


    _is_connected = False
    _is_slewing = False
    _is_tracking = False
    _is_parked = False

    def get_dict(self):
        """
            Return a dictionary containing all of the information
        """
        return {
            "timeout" : self.timeout,
        }

class BasicTelescopeAPI(BasicDeviceAPI):
    """
        Basic Telescope API
    """

    def __init__(self) -> None:
        super().__init__()
    
    def __del__(self) -> None:
        super().__del__()

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