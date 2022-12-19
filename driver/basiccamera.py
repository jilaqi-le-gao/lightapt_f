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

# #################################################################
#
# CameraInfo class used to contain information about camera
#
# #################################################################

class CameraInfo():
    """Camera information class"""

    """Basic Info"""
    _address = None # For ASCOM & INDI
    _name = None
    _api_version : str
    _description : str
    _id : int
    _timeout = 5
    _config_file : str

    """Ability Info"""
    _can_abort_exposure = False
    _can_bin = False
    _can_gain = False
    _can_offset = False
    _can_fast_readout = False
    _can_get_coolpower = False
    _can_guiding = False
    _can_set_temperature = False
    _can_stop_exposure = False
    _has_shutter = False    # 是否有机械快门

    """Status Info"""
    _is_connected = False
    _is_exposure = False
    _is_video = False
    _is_cooling = False
    _is_fastreadout = False
    _is_imgready = False
    _is_guiding = False
    _is_first_image = True

    """properties info"""
    _bayer_offset_x : int
    _bayer_offset_y : int
    _height : int   # In ASCOM CameraYSize
    _width : int    # In ASCOM CameraXSize
    _max_exposure : float
    _min_exposure : float
    _resolution_exposure : float
    _full_capacit : float
    _max_gain : -1
    _min_gain : -1
    _max_offset = -1
    _min_offset = -1
    _highest_temperature : float
    _last_exposure_time : str
    _max_adu : int
    _max_bin_x : int
    _max_bin_y : int
    _subframe_x : int
    _subframe_y : int
    _pixel_height : float # In ASCOM PixelSizeY
    _pixel_width : float # In ASCOM PixelSizeX
    _readout_mode : int
    _readout_modes : list
    _sensor_name : str
    _sensor_type : str
    _start_x : int
    _start_y : int

    """Current Info"""
    _cooling_power : float
    _temperature : float
    _last_exposure : float # 剩余曝光时间
    _gain = -1
    _gains = [-1]
    _bin_x : int
    _bin_y : int
    _offset = -1
    _offsets = [-1]
    _percent_complete : int # 已完成多少进度

    """TODO: What is electrons per ADU"""

    def get_dict(self) -> dict:
        """Return camera infomation in a dictionary"""
        r = {
            "address": self._address,
            "api_version" : self._api_version,
            "description": self._description,
            "id": self._id,
            "timeout" : self._timeout,
            "ability" : {
                "can_stop_exposure" : self._can_stop_exposure,
                "can_abort_exposure" : self._can_abort_exposure,
                "can_guiding" : self._can_guiding,
                "can_binning" : self._can_bin,
                "can_gain" : self._can_gain,
                "can_offset" : self._can_offset,
                "can_set_temperature" : self._can_set_temperature,
                "can_get_coolpower" : self._can_get_coolpower,
                "can_fast_readout" : self._can_fast_readout,
                "has_shutter" : self._has_shutter
            },
            "properties" : {
                "bayer_offset_x" : self._bayer_offset_x,
                "bayer_offset_y" : self._bayer_offset_y,
                "height" : self._height,
                "width" : self._width,
                "max_expansion" : self._max_exposure,
                "min_expansion" : self._min_exposure,
                "resolution_exposure" : self._resolution_exposure,
                "full_capacit" : self._full_capacit,
                "max_gain" : self._max_gain,
                "min_gain" : self._min_gain,
                "max_offset" : self._max_offset,
                "min_offset" : self._min_offset,
                "highest_temperature" : self._highest_temperature,
                "last_exposure_time" : self._last_exposure_time,
                "max_adu" : self._max_adu,
                "max_bin_x" : self._max_bin_x,
                "max_bin_y" : self._max_bin_y,
                "subframe_x" : self._subframe_x,
                "subframe_y" : self._subframe_y,
                "pixel_height" : self._pixel_height,
                "pixel_width" : self._pixel_width,
                "readout_mode" : self._readout_mode,
                "readout_modes" : self._readout_modes,
                "sensor_name" : self._sensor_name,
                "sensor_type" : self._sensor_type,
                "start_x" : self._start_x,
                "start_y" : self._start_y,
            },
            "current" : {
                "cooling_power" : self._cooling_power,
                "temperature" : self._temperature,
                "last_exposure" : self._last_exposure,
                "gain" : self._gain,
                "offset" : self._offset,
                "gains" : self._gains,
                "offsets" : self._offsets,
                "bin_x" : self._bin_x,
                "bin_y" : self._bin_y,
                "percent_complete" : self._percent_complete
            },
            "status" : {
                "exposure" : self._is_exposure,
                "video" : self._is_video,
                "guiding" : self._is_guiding,
                "cooling" : self._is_cooling,
                "fastreadout" : self._is_fastreadout,
                "imgready" : self._is_imgready,
            }
        }
        return r
    
# #################################################################
# 
# Base class for camera control
#
# #################################################################

class BasicCamera(Device):
    """
    Base class for camera control based on Device class
    """

    # #################################################################
    #
    # Base Device class
    #
    # #################################################################

    def __init__(self) -> None:
        """Initialize"""

    def __del__(self) -> None:
        """Destructor"""

    def connect(self,params : dict) -> dict:
        """
            Connect to camera | 连接相机
            Args:
                params (dict): camera parameters
                    {
                        "name" : str # name of the camera
                        "count" : int # number of cameras
                    }
            Returns:
                {
                    "status " : "success","error","warning","debug",
                    "message" : str,
                    "params" : {
                        "info" : CameraInfo object
                        "error" : error message
                        "warning" : warning message
                    }
                }
        """
        return super().connect(params)

    def disconnect(self , params : dict) -> dict:
        """
            Disconnect from camera | 与相机断开连接
            Args:
                None
            Returns:
                {
                    "status" : "success","error","warning","debug",
                    "message" : "Disconnected from camera successfully" # success
                                "Faild to disconnect from camera" # error
                                "Disconnect from camera with warning" # warning
                                "Attempt to disconnect from camera in debug mode" # debug
                    "params" : {
                        "error" : error message
                        "warning" : warning message
                    }
                }
            Note : This function must be called when destory self !
        """
        return super().disconnect({})

    def update_config(self) -> dict:
        """
            Update camera configuration | 更新相机信息
            Args:
                None
            Return:
                {
                    "status" : "success","error","warning","debug",
                    "message" : str,
                    "params" :{
                        "info" : CameraInfo object
                        "error" : error message
                        "warning" : warning message
                    }
                }
            Note : This function usually execute after connection is established
        """
        return super().update_config()

    def set_config(self,params : dict) -> dict:
        """
            Set camera configuration | 设置相机信息
            Args:
                params (dict): camera parameters
            Return:
                {
                    "status" : "success","error","warning","debug",
                    "message" : str
                    "params" :{
                        "error" : error message
                        "warning" : warning message
                    }
                }
        """
        return super().set_config(params)

    def load_config(self, params: dict) -> dict:
        """
            Load the configuration from file
            从文件中加载配置
            @ params : {
                "filename" : filename
                "path" : path
            }
            Return : {
                "status" : "success","error","warning","debug",
                "message" : str,
                "params" : configuration from file
            }
        """
        return super().load_config(params)
        
    def save_config(self) -> dict:
        """
            Save camera configuration | 保存相机配置
            Args:
                None
            Return: {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : None
            }
            Note : This function usually execute before self destory
        """
        return super().save_config()

    def refresh_info(self) -> dict:
        """
            Refresh camera information
            Args:
                None
            Return: {
                "status": "success","error","warning","debug"
                "message" : str
                "params" : {
                    "info": CameraInfo object
                }
            }
        """
        return super().refresh_info()

    # #############################################################
    #
    # Camera control
    #
    # #############################################################

    # #############################################################
    # Exposure functions
    # #############################################################

    def start_exposure(self,params : dict) -> dict:
        """
            Start exposure | 开始曝光\n
            Args:
                params (dict): camera parameters
                    {
                        "exposure" : float # must > 0
                        "gain" : int # like brightness
                        "offset" : int # must > 0
                        "binning" : int # Merge pixel values
                        "img" : {
                            "is_save" : boolean # Will save image
                            "filename" : str # Filename to save
                            "is_flip" : boolean # Will flip image
                            "type" : str # Type of image , like "Fits" or "Tiff" or "JPEG"
                        },
                        "roi" : {
                            "start_x" : int # Start x position of image
                            "start_y" : int # Start y position of image
                            "height" : int # Height of image
                            "width" : int # Width of image
                        }
                    }
            Return: {
                "status" : "success","error","warning","debug"
                "message" : "Camera exposure successful" # success
                            "Faild to finish exposure" # error
                            "Camera finish exposure with warning" # warning
                            "Attempting to get camera exposure in debug mode" # debug
                "params" : {
                    "error" : error message
                    "warning" : warning message
                }
            }
            Note : Must make sure camera is safely configured
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def abort_exposure(self) -> dict:
        """
            Abort exposure | 停止曝光
            Args:
                None
            Return: {
                "status" : "success","error","warning","debug"
                "message" : "Aborted exposure successfully" # success
                            "Faild to abort exposure" # error
                            "Aborted exposure with warning" # warning
                            "Attempting to abort exposure in debug mode" # debug
                params: None
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def get_exposure_status(self) -> dict:
        """
            Get exposure status | 获取曝光状态
            Args:
                None
            Return : {
                "status" : "success","error","warning","debug"
                "message" : "Camera is exposuring..." # success
                            "Camera is idle"
                            "Camera is in error status"
                            "Faild to get camera exposure status" # error
                            "Get camera exposure status with warning" # warning
                            "Attempting to get camera exposure status in debug mode" # debug 
                "params" : {
                    "status" : boolean # True if camera is exposuring
                    "error" : str # None if success
                    "warning" : str # None if success
                }
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def get_exposure_result(self) -> dict:
        """
            Get exposure data | 获取图像数据
            Args:
                None
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : {
                    "data" : {
                        "img" : bufferarray
                        "width" : int
                        "height" : int
                        "size" : int
                        "bayer" : {
                            "enable" : boolean
                            "mode" : str # Like RGB or RGBA
                        }
                    }
                }
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def save_image(self, params : dict) -> dict:
        """
            Save exposure image
            Args:
                params (dict): image parameters
                {
                    "filename": str
                    "type": str # Like FITS or JPEG or TIFF
                    "img" : bufferarray
                    "width" : int
                    "height" : int
                    "size" : int
                    "bayer" : {
                        "enable" : boolean
                        "mode" : str # Like RGB or RGBA
                    },
                    "info" : list # For Fits title
                }
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : None
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))
    
    # #############################################################
    # Video functions
    # #############################################################

    def start_video(self,params : dict) -> dict:
        """
            Start video | 开始视频拍摄
            Args:
                params (dict): camera parameters
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : {

                }
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))
    
    def abort_video(self) -> dict:
        """
            Abort the video capture | 停止视频拍摄
            Args:
                None
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params: None
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def get_video_status(self) -> dict:
        """
            Get video capture status | 获取视频录制状态
            Args:
                None
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : {
                    "drop_frames" : int
                    "size" : int
                    "fps" : int
                }
            }
            Note : This function is not surely can be called
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def get_video_data(self) -> dict:
        """
            Get video data | 获取视频数据
            Args:
                None
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : {
                    "drop_frames" : int
                    "size" : int
                    "data" : bufferarray
                }
            }
            TODO : I'm not sure how to save a video file
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def save_video(self,params : dict) -> dict:
        """
            Save video | 开始视频拍摄
            Args:
                params (dict): video parameters
                {
                    "filename": str
                    "type": str # Like MP4
                    "fps": int
                }
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : None
            }
            TODO : What parameters does saving video need?
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    # #############################################################
    # Cooler functions
    # #############################################################

    def cool(self,params : dict) -> dict:
        """
            Cool on/off | 开始或停止制冷 
            Args:
                params (dict): camera parameters
                {
                    "enable" : boolean
                }
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : None
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def get_cool_status(self) -> dict:
        """
            Get the status of the cooler
            Args:
                None
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : {
                    "enable" : boolean
                }
            }
            Note : This is only available for the cooler camera !
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def get_temperature(self) -> dict:
        """
            Get camera temperature | 获取相机温度
            Note : This is available for almost all cameras
            Args:
                None
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : {
                    "temperature" : float
                }
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    def set_temperature(self,params : dict) -> dict:
        """
            Set camera temperature | 设置相机温度
            Note : This is available for almost all cameras
            Args:
                params (dict): camera parameters
                {
                    "temperature" : float
                }
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : None
            }
            Note : This is only available for cooler cameras !
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    # #############################################################
    # Information functions
    # #############################################################

    @property
    def gain(self) -> dict:
        """
            Get camera gain | 获取相机增益
            Args:
                None
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : {
                    "gain" : float
                }
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))
    
    @gain.setter
    def gain(self,params : dict) -> dict:
        """
            Set camera gain | 设置相机增益
            Args:
                params (dict): gain parameters
                {
                    "gain" : float
                }
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : None
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    @property
    def offset(self) -> dict:
        """
            Get camera offset | 获取相机偏置
            Args:
                None
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : {
                    "offset" : float
                }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))
    
    @offset.setter
    def offset(self,params : dict) -> dict:
        """
            Set the offset | 设置相机偏置
            Args:
                params (dict): offset parameters
                {
                    "offset" : float
                }
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : None
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    @property
    def gamma(self) -> dict:
        """
            Get camera gamma | 获取相机伽马值
            Args:
                None
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : {
                    "gamma" : float
                }
            }
            Note : This function need camera support , ASI camera is surely support.
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    @gamma.setter
    def gamma(self,params : dict) -> dict:
        """
            Set camera gamma | 设置相机伽马值
            Args:
                params (dict): gamma parameters
                {
                    "gamma" : int
                }
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : None
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    @property
    def binning(self) -> dict:
        """
            Get the binning mode | 获取像素合成模式
            Args:
                None
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : {
                    "binning" : int # 1 or 2 or 4
                    Note : If bin is bigger than 4 , everyone will thank you
                }
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    @binning.setter
    def binning(self,params : dict) -> dict:
        """
            Set the binning mode | 设置像素合成
            Args:
                params (dict): binning parameters
                {
                    "binning" : int # 1 or 2 or 4
                }
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : None
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    @property
    def roi(self) -> dict:
        """
            Get the roi | 获取相机画幅
            Args:
                None
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : {
                    "roi" : {
                        "start_x" : int
                        "start_y" : int
                        "height" : int
                        "width" : int
                        "is_filp" : boolean # This need camera support
                    }
                }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

    @roi.setter
    def roi(self, params : dict) -> dict:
        """
            Set the roi | 设置相机画幅
            Args:
                params (dict): roi parameters
                {
                    "roi" : {
                        "start_x" : int
                        "start_y" : int
                        "height" : int
                        "width" : int
                        "is_filp" : boolean # This need camera support
                    }
                }
            Return : {
                "status" : "success","error","warning","debug"
                "message" : str
                "params" : None
            }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"))

