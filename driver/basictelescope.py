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

import ephem

__api__ = "Telescope Basic API"
__api_version__ = "1.0.0"
__copyright__ = "Max Qian"
__license__ = "GPL3"

# #########################################################################
# 
# Telescope Info Class
#
# #########################################################################

class TelescopeInfo():
    """Telescope information"""

    """Basic Info"""
    _address = None # For ASCOM & INDI
    _name = None
    _api_version : str
    _description : str
    _id : int
    _coordinates_type : int
    _timeout = 5
    _config_file : str

    """Ability Info"""
    _can_slewing = False
    _can_park = False
    _can_unpark = False
    _can_home = False
    _can_tracking = False
    _can_guiding = False

    _can_set_park = False
    _can_set_home = False
    _can_set_ra_rate = False
    _can_set_dec_rate = False

    """Property Info"""
    _lat : str
    _lon : str
    _tracking_ra_rate : float
    _tracking_dec_rate : float
    _guiding_ra_rate : float
    _guiding_dec_rate : float
    _slewing_ra_rate : float
    _slewing_dec_rate : float

    """Current Info"""
    _ra : str
    _dec : str
    _az : str
    _alt : str
    _convert_ra : str
    _convert_dec : str
    _convert_az : str
    _convert_alt : str

    """Status Info"""
    _is_connected = False
    _is_operating = False
    _is_parked = False
    _is_home = False
    _is_tracking = False
    _is_slewing = False
    _is_guiding = False

    def get_dict(self) -> dict:
        """Return telescope information in a dictionary"""
        r = {
            "address": self._address,
            "api_version" : self._api_version,
            "description": self._description,
            "id": self._id,
            "coordinates_type": self._coordinates_type,
            "timeout" : self._timeout,
            "ability" : {
                "can_slewing": self._can_slewing,
                "can_park" : self._can_park,
                "can_unpark" : self._can_unpark,
                "can_home" : self._can_home,
                "can_tracking" : self._can_tracking,
                "can_guiding" : self._can_guiding,
                "can_set_park" : self._can_set_park,
                "can_set_home" : self._can_set_home,
                "can_set_ra_rate" : self._can_set_ra_rate,
                "can_set_dec_rate" : self._can_set_dec_rate
            },
            "property" : {
                "lon" : self._lon,
                "lat" : self._lat,
                "tracking_ra_rate" : self._tracking_ra_rate,
                "tracking_dec_rate" : self._tracking_dec_rate,
                "guiding_ra_rate" : self._guiding_ra_rate,
                "guiding_dec_rate" : self._guiding_dec_rate,
                "slewing_ra_rate" : self._slewing_ra_rate,
                "slewing_dec_rate" : self._slewing_dec_rate
            },
            "current" : {
                "ra" : self._ra,
                "dec" : self._dec,
                "az" : self._az,
                "alt" : self._alt,
                "convert" : {
                    "ra" : self._convert_ra,
                    "dec" : self._convert_dec,
                    "az" : self._convert_az,
                    "alt" : self._convert_alt
                }
            },
            "status" : {
                "is_connected" : self._is_connected,
                "is_parked" : self._is_parked,
                "is_home" : self._is_home,
                "is_slewing" : self._is_slewing,
                "is_tracking" : self._is_tracking,
                "is_guiding" : self._is_guiding
            }
        }
        return r

# #########################################################################
# 
# Basic Telescope Class
#
# #########################################################################

class BasicTelescope(Device):
    """
    Basic Telescope class.Every telescope object should parent this class.\n
    基础的赤道仪类，所有赤道仪驱动都需要从此处派生，提供了最基础的模板。
    """

    # #########################################################################
    #
    # From Device Class | 继承设备类的函数
    #
    # #########################################################################

    def __init__(self) -> None:
        """Construct | 构造函数"""

    def __del__(self) -> None:
        """Delete | 析构函数"""

    def connect(self, params: dict) -> dict:
        """
            Connect to telescope and after success we can do anything else
            连接望远镜，连接完成后理应不需要再执行任何有关于连接或者初始化的函数
            @ params : {
                "count": int # the number of telescope
                "name" : string # the name of the telescope
            }
            @ return : {
                "status" : "success","error","warning","debug"
                "message": str
                "params" : {
                    "id" : int # the id of the device
                    "name" str # the name of the device
                }
            }
        """
        return super().disconnect(params)

    def disconnect(self, params: dict) -> dict:
        """
            Disconnect from the telescope after disconnection we can do nothing with telescope
            与望远镜断开连接，完成后就无法再对望远镜进行操作，理应释放所有相关资源，避免内存浪费
            @ return : {
                "status" : "success","error","warning","debug",
                "message" : str,
                "params" : None
            }
        """
        return super().disconnect(params)

    def return_message(self, status: str, message: str, params={}) -> dict:
        """Return message just use parent class | 同设备类"""
        return super().return_message(status, message, params)

    def update_config(self) -> dict:
        """
            Update Telescope configuration and storage settings in Telescope_Info\n
            Run this function when first initialize the telescope\n
            更新望远镜配置，需要获取所有需要的参数，并且最好存储在TelescopeInfo中\n
            在第一次初始化赤道仪时执行\n
            @ params : None
            @ return : {
                "status" : "success","error","warning","debug",
                "message" : str,
                "params" : {
                    "info" : TelescopeInfo object
                }
            }
            Note : This function needs to be called
        """
        return super().update_config()

    def load_config(self, params: dict) -> dict:
        """
            Load the configuration from file
            从文件中加载配置
            @ params : {
                "filename" : filename
                "path" : path
            }
            @ return : {
                "status" : "success","error","warning","debug",
                "message" : str,
                "params" : configuration from file
            }
        """
        return super().load_config(params)

    def save_config(self) -> dict:
        """
            Save the configuration from Telescope_Info as a JSON file
            将Telescope_Info中的参数保存到对应的JSON文件中
            @ params : None
            @ return : {
                "status" : "success","error","warning","debug",
                    # Success : save the configuration to file successfully
                    # Error : save the configuration to file with error
                    # Warning : save the configuration to file with warning
                    # Debug : save the configuration to file in debug mode
                "message" : str,
                "params" : None
            }
        """
        return super().save_config()

    def refresh_info(self) -> dict:
        """
            Refresh the Info from Telescope_Info, other functions get information through this function
            其他函数通过此函数读取信息
            @ params : None
            @ return : {
                "status" : "success","error","warning","debug",
                    # Success : refresh telescope info successfully
                    # Error : refresh telescope info with error
                    # Warning : refresh telescope info with warning
                    # Debug : refresh telescope info in debug mode
                "message" : str,
                "params" : {
                    "info" : TelescopeInfo object
                }
            }
        """
        return super().refresh_info()

    # #################################################################
    # 
    # Telescope Class | 赤道仪类独有的函数
    #
    # #################################################################

    # #############################################################
    # Goto functions
    # #############################################################

    def goto(self,params : dict) -> dict:
        """
            Goto the specified position and return the result in dict format.
            After executing this function we should finish all of the processes to do about the goto
            If necessary , we should not change the settings.\n
            Goto功能,执行后应该完成所有与Goto相关的事项，包括设置的修改，如有需要应该恢复Goto前设置
            @ params : {
                "j2000" : boolean # True if the coordinates given are in the format of J2000
                "RA" : str # Just like xx:xx:xx
                "DEC" : str # Just like xx:xx:xx
            }
            @ return : {
                "status" : "success","error","warning","debug"
                    # Success : goto successfully
                    # Error : goto with error
                    # Warning : goto with warning
                    # Debug : goto in debug mode
                "message" : str
                "params" : {
                    # After goto successfully , should return the current coordinates. \n
                    The coordinates should be in the format of string
                    "RA" : str
                    "DEC" : str
                }
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def abort_goto(self) -> dict:
        """
            Abort Goto if the function is called
            停止Goto，可能会涉及到线程调度，有待思考
            @ return : {
                "status" : "success","error","warning","debug"
                    # Success : abort goto successfully
                    # Error : abort goto with error
                    # Warning : abort goto with warning
                    # Debug : abort goto in debug mode
                "message" : str
                "params" : None
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def get_coordinates(self) -> dict:
        """
            Get the coordinates of the telescope | 获取赤道仪当前指向坐标
            @ return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : {
                    "j2000" : boolean # True if the coordinates given are in the format of J2000
                    "RA" : str
                    "DEC" : str
                }
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def get_location(self) -> dict:
        """
            Get the location of the telescope | 获取赤道仪当前地理坐标
            Return error : if telescope is not available to get location
            Return warning : if the location is not correct
            Return debug : I don't know
            @ return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : {
                    "longitude" : str
                    "latitude" : str
                }
            }
        """
        """Note : This method needs telescope support"""
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    # #############################################################
    # Tracking functions
    # #############################################################

    def tracking(self, params : dict) -> dict:
        """
            Start tracking | 开始跟踪
            @params : {
                "mode" : str # sun moon star planet tracking mode
                "speed" : float # speed of tracking
            }
            @ return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : None
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def abort_tracking(self) -> dict:
        """ 
            Abort tracking | 停止跟踪
            @ return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : None
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def get_tracking_info(self) -> dict:
        """
            Get the tracking information
            @ params : None
            @ return : {
                "status" : "success","error","warning","debug"
                "message" : str,
                "params" : {
                    "is_tracking" : boolean # True if tracking
                    "mode" : str, # like "moon" or "sun" or "star"
                    "speed" : float
                }
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def set_tracking_settings(self, params : dict) -> dict:
        """
            Set the tracking settings | 设置望远镜跟踪设置
            @ params : {
                "mode" : str,
                "speed" : float,
            }
            @ return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : None
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    # #############################################################
    # Sync functions
    # #############################################################
    def sync(self , params : dict) -> dict:
        """Sync the Telescope (What does this do?) | 难以解释"""
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def abort_sync(self) -> dict:
        """Abort the current sync operation"""
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    # #############################################################
    # Guide functions
    # #############################################################

    def guide(self,params : dict) -> dict:
        """
            Start the guide and return the result | 开始导星并且返回初始化状态
            @ params : {
                "mode" : str,
                "software" : str # PHD2 or Linguider
                "min_version" : str # minimum version of the software
                "max_version" : str # maximum version of the software
                "properties" : {
                    "camera" : str # camera . always guide camera
                    "telescope" : str # telescope
                }
                "guiding" : {
                    "exposure" : float
                    "gain" : float
                    "dither" : boolean
                    "dark" : boolean
                }
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def abort_guide(self) -> dict:
        """
            Stop the guide and return the result | 停止导星
            @ params : None
            @ return : {
                "status" : "success","error","warning","debug"
                    # Success : abort guiding successfully
                    # Error : abort guiding with error
                    # Warning : abort guiding with warning
                    # Debug : abort guiding in debug mode
                "message" : str
                "params" : None
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    # #############################################################
    # Park function
    # #############################################################

    def park(self) -> dict:
        """
            Park the telescope,we should not use telescope again until after unpark is called | 归位
            @ params : None
            @ return : {
                "status" : "success","error","warning","debug"
                    # Success : park the telescope successfully
                    # Error : park the telescope with error
                    # Warning : park the telescope with warning
                    # Debug : park the telescope in debug mode
                "message" : str
                "params" : None
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def unpark(self) -> dict:
        """
            Unpark the telescope | 解除归位状态
            @ params : None
            @ return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : None
            }
        """     
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def get_park_position(self) -> dict:
        """
            Get the park position | 获取归位位置
            @ params : None
            @ return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : None
            }
            Note : This method needs telescope support
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def set_park_position(self, params : dict) -> dict:
        """
            Set the park position | 设置归位位置
            @ params : {
                "RA" : str
                "DEC" : str
            }
            @ return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : None
            }
            Note : This method needs telescope support and is a little bit dangerous
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    # #############################################################
    # Home function
    # #############################################################

    def home(self) -> dict:
        """
            Home the telescope | 赤道仪回家咯
            @ params : None
            @ return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : None
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def unhome(self) -> dict:
        """
            Unhome the telescope | ?
            @ params : None
            @ return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : None
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def get_home_position(self) -> dict:
        """
            Get the home position | 获取家的位置
            @ params : None
            @ return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : {
                    "RA" : str
                    "DEC" : str
                }
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def set_home_position(self) -> dict:
        """
            Set the home position | 设置家的位置
            @ params : {
                "RA" : str
                "DEC" : str
            }
            @ return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : None
            }
            Note : This method needs telescope support.\n
            Most of the iOptron telescopes support this.
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    # #############################################################
    # 
    # Useful functions
    #
    # #############################################################

    def calc_coordinates(self,params : dict) -> dict:
        """
            Calculate the coordinates of the observer for the given parameters
            计算坐标
            @ params : {
                "type" : str # "h" | "s" The type you want to convert to
                "RA" : str | float # hourangle or just a float value
                "DEC" : str | float # hourangle or just a float value
            }
            @ return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : {
                    "RA" : str | float
                    "DEC" : str | float
                }
            }
        """
        if params.get("type") == "h":
            ra,dec = params.get("RA"),params.get("DEC")
            if not isinstance(ra,float) or not isinstance(dec,float):
                log.loge(_("Error: RA or DEC must be float if you are using hourangle mode"))
                return self.return_message("error",_("Error: RA or DEC must be float"),_("Change a type"))
            """Convert coordinates from degrees to hourangle"""
            def calc_coordinates(coordinates) -> str:
                """Convert coordinates from degrees to hourangle"""
                coordinates_sign = "+"
                """For DEC coordinates convert"""
                if coordinates < 0:
                    coordinates_sign = ""
                coord_h = int(coordinates)
                coord_m = int((coordinates - coord_h) * 60)
                coord_s = int((coordinates - coord_h - coord_m / 60) * 3600)
                coord_h,coord_m,coord_s = map(str,[coord_h,coord_m,coord_s])
                return coordinates_sign + coord_h + ":" + coord_m + ":" + coord_s
            ra = calc_coordinates(ra)
            dec = calc_coordinates(dec)
            return self.return_message("success",_("calc coordinates from float to hourangle"),{"RA" : ra, "DEC" : dec})
        elif params.get("type") == "s":
            ra,dec = params.get("RA"),params.get("DEC")
            if not isinstance(ra,str) or not isinstance(dec,str):
                log.loge(_("Error: RA or DEC must be string if you are using string mode"))
                return self.return_message("error",_("Error: RA or DEC must be string"),_("Change a type"))
            """Convert coordinates from hourangle to string"""
            def calc_coordinates(coordinates : str) -> float:
                coordinates_sign = None
                """For DEC coordinates convert"""
                if coordinates[0] == "-" or coordinates[0] == "+":
                    coordinates_sign = coordinates[0]
                    coordinates = coordinates[1:]
                coord_h,coord_m,coord_s = map(int,coordinates.split(":"))
                coord = coord_h + coord_m / 60 + coord_s / 3600
                if coordinates_sign == "-":
                    coord = -coord
                return "%.14f"%coord
            ra = calc_coordinates(ra)
            dec = calc_coordinates(dec)
            return self.return_message("success",_("calc coordinates from hourangle to string"),{"RA" : ra, "DEC" : dec})
        else:
            log.loge(_("Error: Invalid type"))
            return self.return_message("error",_("Error: Invalid type"))

    def calc_coordinates_j(self,params : dict) -> dict:
        """
            Calculate coordinates from given parameters in the given coordinate system
            @params : {
                "type" : str # "JNow" | "J2000" The type you want to convert
                "RA" : str | float # hourangle or just a float value
                "DEC" : str | float # hourangle or just a float value
            }
            @ return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : {
                    "RA" : str
                    "DEC" : str
                }
            }
        """
        ra,dec = params.get("RA"),params.get("DEC")
        """TODO: When DEC is negative number what should I do here"""
        if params.get("type") == "JNow":
            center_J2000 = ephem.Equatorial(ra,dec,epoch = ephem.J2000)
            center_JNow = ephem.Equatorial(center_J2000, epoch=ephem.now())            
        elif params.get("type") == "J2000":
            center_JNow = ephem.Equatorial(ra,dec,epoch = ephem.now())
            center_J2000 = ephem.Equatorial(center_JNow , epoch = ephem.J2000)
        else:
            log.loge(_("Error: Invalid type"))
            return self.return_message("error",_("Invalid type"))
        ra_h,ra_m,ra_s = str(center_JNow.ra).split(":")
        ra_s = str(int(round(float(ra_s))))
        ra = ra_h + ":" + ra_m + ":" + ra_s        
            
        dec_h,dec_m,dec_s = str(center_JNow.dec).split(":")
        dec_s = str(int(round(float(dec_s))))
        dec = dec_h + ":" + dec_m + ":" + dec_s
        return self.return_message("success", _("Calculate success"),{"RA" : ra, "DEC" : dec})