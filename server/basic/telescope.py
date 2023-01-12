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

    # Basic telescope infomation
    _ipaddress : str # IP address only ASCOM and INDI
    _api_version : str # API version only ASCOM and INDI
    _name : str # name of the camera
    _id : int # id of the camera
    _description : str
    _configration = "" # path to the configuration file

    coord_system : int # the coordinate system . This is also a important parameter , 1 is JNonw ,2 is J2000 , will other type of coordinate system be supported

    # Timeout of all of the commands
    timeout = 60

    # Current telescope target coordinates , I was not sure what is the difference between current coordinates and target coordinates
    ra = ""
    dec = ""
    # The following two parameters need telescope has az/alt mode , most of the GEM do not support this
    az = ""
    alt = ""
    # If the GPS is enabled
    lon = ""
    lat = ""

    # TODO : I don't know what will happen if we connect a single axis telescope like SGP

    # Slewing speed , in iOptron is 1x,2x,4x ...
    # NOTE : Why I use flaot there? Because in Alpaca the return is not the value like 1x or 128x
    #       It returns the degrees per second the telescop will slew , so there must have a convert system
    slewing_ra_rate : list
    slewing_dec_rate : list
    # This is for telescope safety
    max_slewing_ra_rate : float
    max_slewing_dec_rate : float
    min_slewing_ra_rate : float
    min_slewing_dec_rate : float
    # Tracking mode , such as star,sun or moon
    track_mode : int
    # Tracking rate of the RA and DEC axis
    track_ra_rate : float
    track_dec_rate : float

    # RA and DEC axis park settings 
    park_ra = 0
    park_dec = 0

    # Can telescope goto , most of them have this function
    _can_goto = False
    # Can telescope operation been aborted , this is for safety
    _can_ahort_goto = False
    # NOTE : This is add on 2023/1/10 , I think we need to think about if the telescope do not have DEC axis
    _can_dec_axis = False
    # Can telescope sync the current target
    _can_sync = False
    # Can telescope RA axis track
    _can_ra_track = False
    # Can telescope DEC axis track
    _can_dec_track = False
    # Can telescope park , not sure that every telescope supports this
    _can_park = False
    # Can set telescope parking postion
    _can_set_park_postion = False
    # Same as _can_park
    _can_home = False
    # Can set RA axis tracking rate (speed) , this surely need _can_track is True
    _can_set_track_ra_rate = False
    # Can set DEC axis tracking rate (speed), this surely need _can_track is True
    _can_set_track_dec_rate = False
    # Can set traking mode like sun,star or moon , even if the custom tracking mode
    _can_set_track_mode = False
    # Can telescope track a satellite , this means that the telescope can slewing quickly enough
    _can_track_satellite = False
    # Can get telescope location , if we have these attributes , we can better deal with coordinates
    _can_get_location = False
    # Is the telescope have AZ/ALT mode , this is not surely been enabled 
    _can_az_alt = False

    # Is the telescope connected , if not , how we communicate with the telescope
    _is_connected = False
    # Is the telescope slewing such as goto or sync , make sure that the command will not be too many at one time
    _is_slewing = False
    # Is the telescope tracking , this is very important for deepsky photograph
    _is_tracking = False
    # Is the telescope parked, if the status is true , do not do anything until unpark
    _is_parked = False
    # Is the telescope at the home position
    _is_homed = False

    def get_dict(self):
        """
            Return a dictionary containing all of the information
        """
        return {
            "ipaddress" : self._ipaddress,
            "api_version" : self._api_version,
            "name" : self._name,
            "id" : self._id,
            "description" : self._description,
            "configration" : self._configration,
            "timeout" : self.timeout,
            "current" : {
                "ra" : self.ra,
                "dec" : self.dec,
                "az" : self.az,
                "alt" : self.alt,
            },
            "location" : {
                "lat" : self.lat,
                "lon" : self.lon,
            },
            "slewing" : {
                "ra" : {
                    "max" : self.max_slewing_ra_rate,
                    "min" : self.min_slewing_ra_rate
                },
                "dec" : {
                    "max" : self.max_slewing_dec_rate,
                    "min" : self.min_slewing_dec_rate
                }
            },
            "tracking" : {
                "mode" : self.track_mode,
                "ra" : self.track_ra_rate,
                "dec" : self.track_dec_rate
            },
            "parking" : {
                "ra" : self.park_ra,
                "dec" : self.park_dec,
            },
            "abilities" : {
                "can_goto" : self._can_goto,
                "can_abort_goto" : self._can_ahort_goto,
                "can_home" : self._can_home,
                "can_park" : self._can_park,
                "can_dec_axis" : self._can_dec_axis,
                "can_sync" : self._can_sync,
                "can_ra_track" : self._can_ra_track,
                "can_dec_track" : self._can_dec_track,
                "can_set_park_position" : self._can_set_park_postion,
                "can_set_track_ra_rate" : self._can_set_track_ra_rate,
                "can_set_track_dec_rate" : self._can_set_track_dec_rate,
                "can_set_track_mode" : self._can_set_track_mode,
                "can_track_satellite" : self._can_track_satellite,
                "can_get_location" : self._can_get_location,
                "can_az_alt" : self._can_az_alt
            }
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
                status : int
                message : str
                params : 
                    ra : str
                    dec : str
                    az : str
                    alt : str
            NOTE : This function is suggested to be called after sync process is finished
        """

    def park(self) -> dict:
        """
            Park the telescope to default position\n
            Args : None
            Returns : 
                status : int
                message : str
                params : None
            NOTE : After execution of this function , we can not control the telescope until we unpark the telescope
        """

    def unpark(self) -> dict:
        """
            Unpark the telescope\n
            Args : None
            Returns :
                status : int
                message : str
                params : None
            NOTE : Just like the above function
        """

    def get_park_position(self) -> dict:
        """
            Get the parking position of the telescope
            Args : None
            Returns : 
                status : int
                message : str
                params : dict
                    position : int or list
        """

    def set_park_position(self , params : dict) -> dict:
        """
            Set the parking position of the telescope
            Args : 
                params : dict
                    ra : str
                    dec : str
            Returns :
                status : int
                message : str
                params : None
        """

    def home(self) -> dict:
        """
            Let the telescope to go home position
            Args : None
            Returns :
                status : int
                message : str
                params : None
            NOTE : This function is not like park() , after this we can still control the telescope
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