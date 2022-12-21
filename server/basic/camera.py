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

class BasicCameraInfo(object):
    """
        Basic camera information container
    """

    _type = "" # type of the camera , must be given
    _name : str # name of the camera
    _id : int # id of the camera
    _description : str
    _timeout = 5
    _configration = "" # path to the configuration file

    _exposure = 0
    _gain = 0
    _offset = 0
    _iso = 0
    _binning = []
    _temperature = -256
    _cool_power = 0
    _last_exposure : float
    _percent_complete : float

    _image_id = 0
    _image_path = ""
    _image_type = ""
    _image_name_format = ""

    _ipaddress : str # IP address only ASCOM and INDI
    _api_version : str # API version only ASCOM and INDI

    _can_binning : bool
    _can_cooling : bool
    _can_gain : bool
    _can_get_coolpower : bool
    _can_guiding : bool
    _can_has_shutter : bool
    _can_iso : bool
    _can_offset : bool
    _can_save = True

    _is_color : bool
    _is_connected : bool
    _is_cooling : bool
    _is_exposure : bool
    _is_guiding : bool
    _is_imageready : bool
    _is_video : bool

    _max_gain : int
    _min_gain : int
    _max_offset : int
    _min_offset : int
    _max_exposure : float
    _min_exposure : float
    _min_exposure_increment : float
    _max_binning : list

    _height : int
    _width : int
    _max_height : int
    _min_height : int
    _max_width : int
    _min_width : int
    _depth : int
    _max_adu : int
    _imgarray = False    # Now is just for ASCOM
    _bayer_pattern : int
    _bayer_offset_x : int
    _bayer_offset_y : int
    _pixel_height : float
    _pixel_width : float
    _start_x : int
    _start_y : int
    _subframe_x : int
    _subframe_y : int
    _sensor_type : str
    _sensor_name : str

    def get_dict(self) -> dict:
        """
            Returns a dictionary containing camera information
            Args : None
            Returns : dict
        """
        return {
            "type": self._type,
            "name": self._name,
            "id": self._id,
            "description": self._description,
            "timeout": self._timeout,
            "configration": self._configration,
            "current" : {
                "exposure": self._exposure,
                "gain": self._gain,
                "offset": self._offset,
                "iso": self._iso,
                "binning": self._binning,
                "temperature": self._temperature,
                "cool_power": self._cool_power,
            },
            "ability": {
                "can_binning" : self._can_binning,
                "can_cooling" : self._can_cooling,
                "can_gain" : self._can_gain,
                "can_get_coolpower" : self._can_get_coolpower,
                "can_guiding" : self._can_guiding,
                "can_has_shutter" : self._can_has_shutter,
                "can_iso" : self._can_iso,
                "can_offset" : self._can_offset,
            },
            "status" : {
                "is_connected" : self._is_connected,
                "is_cooling" : self._is_cooling,
                "is_exposure" : self._is_exposure,
                "is_guiding" : self._is_guiding,
                "is_imageready" : self._is_imageready,
                "is_video" : self._is_video,
            },
            "properties" : {
                "max_gain" : self._max_gain,
                "min_gain" : self._min_gain,
                "max_offset" : self._max_offset,
                "min_offset" : self._min_offset,
                "max_exposure" : self._max_exposure,
                "min_exposure" : self._min_exposure,
                "max_binning" : self._max_binning,
            },
            "frame" : {
                "height" : self._height,
                "width" : self._width,
                "max_height" : self._max_height,
                "min_height" : self._min_height,
                "max_width" : self._max_width,
                "min_width" : self._min_width,
                "depth" : self._depth if self._depth is not None else 0,
                "max_adu" : self._max_adu,
                "imgarray" : self._imgarray,
                "bayer_pattern" : self._bayer_pattern,
                "bayer_offset_x" : self._bayer_offset_x,
                "bayer_offset_y" : self._bayer_offset_y,
                "pixel_height" : self._pixel_height,
                "pixel_width" : self._pixel_width,
                "start_x" : self._start_x,
                "start_y" : self._start_y,
                "subframe_x" : self._subframe_x,
                "subframe_y" : self._subframe_y,
                "sensor_type" : self._sensor_type,
                "sensor_name" : self._sensor_name,
            },
            "network" : {
                "ipaddress" : self._ipaddress,
                "api_version" : self._api_version,
            }
        }

class BasicSequenceInfo(object):
    """
        Basic sequence information container
    """

    sequence_count = 0
    sequence = []

    def get_dict(self) -> dict:
        """
            Returns a dictionary containing basic sequence information
            Args : None
            Returns : dict
        """
        return {
            "sequence_count" : self.sequence_count,
            "sequence" : self.sequence,
        }

class BasicCameraAPI(BasicDeviceAPI):
    """
        Basic Camera API
    """

    def __init__(self) -> None:
        super().__init__()

    def __del__(self) -> None:
        return super().__del__()

    # #################################################################
    #
    # Camera Basic API
    #
    # #################################################################

    def start_exposure(self, params : dict) -> dict:
        """
            Start exposure function | 开始曝光
            Args : {
                "params" : {
                    "exposure" : float # exposure time
                    "gain" : int # gain
                    "offset" : int # offset
                    "binning" : int # binning
                    "image" : {
                        "is_save" : bool
                        "name" : str
                        "type" : str # fits or tiff of jpg
                    }
                    "filterwheel" : {
                        "enable" : boolean # enable or disable
                        "filter" : int # id of filter
                    }
                }
            }
            Returns : {
                "status" : int ,
                "message" : str,
                "params" : None
            }
        """

    def abort_exposure(self) -> dict:
        """
            Abort exposure function | 关闭曝光
            Args:
                None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    def get_exposure_status(self) -> dict:
        """
            Get exposure status function | 获取曝光状态
            Args:
                None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : Exposure Status Object
                }
            }
            NOTE : This function should not be called if the camera is not in exposure
        """

    def get_exposure_result(self) -> dict:
        """
            Get exposure result function | 获取曝光结果
            Args:
                None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "image" : Base64 Encode Image Data,
                    "histogram" : List,
                    "info" : dict
                }
            }
        """

    def start_sequence_exposure(self , params : dict) -> dict:
        """
            Start exposure function | 开始计划曝光
            Args : {
                "params" : {
                    "exposure" : float # exposure time
                    "gain" : int # gain
                    "offset" : int # offset
                }
            }
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "results" : SeqExposureResults
                }
            }
            TODO : Args and Returns should be thinked more carefully
        """

    def abort_sequence_exposure(self) -> dict:
        """
            Abort sequence exposure | 停止计划拍摄
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
            NOTE : This function should not be called if the camera is not in exposure
        """

    def pause_sequence_exposure(self) -> dict:
        """
            Pause sequence exposure | 停止计划拍摄 (Can continue)
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """
    
    def continue_sequence_exposure(self) -> dict:
        """
            Continue sequence exposure | 继续计划拍摄
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    def get_sequence_exposure_status(self) -> dict:
        """
            Get exposure status function | 获取计划拍摄状态
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : Exposure Status Object
                }
            }
        """

    def get_sequence_exposure_result(self) -> dict:
        """
            Get the sequence exposure result | 获取计划拍摄结果
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "image" : Base64 Encode Image Data List
                    "histogram" : List,
                    "info" : dict
                }
            }
            NOTE : This function should be thinked carefully
        """

    def cooling(self, params : dict) -> dict:
        """
            Cooling function | 制冷
            Args : {
                "params" : {
                    "enable" : boolean
                }
            }
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : Cooling Status Object
                }
            }
            NOTE : This function needs camera support
        """

    def cooling_to(self, params : dict) -> dict:
        """
            Cooling to temperature function | 制冷到指定温度
            Args : {
                "params" : {
                    "temperature" : float
                }
            }
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : Cooling Status Object
                }
            }
            NOTE : This function needs camera support
        """

    def get_cooling_status(self) -> dict:
        """
            Get cooling status function | 获取当前制冷状态
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : Cooling Status Object
                }
            }
            NOTE : This function needs camera support
        """

    def start_video_capture(self, params : dict) -> dict:
        """
            Start video capture function | 开始录制视频
            Args : {
                "params" : {
                    "path" : str
                }
            }
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    def abort_video_capture(self) -> dict:
        """
            Abort video capture function | 停止录制视频
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """

    def get_video_capture_status(self) -> dict:
        """
            Get video capture status function | 获取录制视频状态
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : Video Capture Status Object
                }
            }
        """

    def get_video_capture_result(self) -> dict:
        """
            Get video capture result | 获取视频录制结果
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "video" : Video 
                }
            }
        """

    # #################################################################
    #
    # Camera Current Information
    #
    # #################################################################

    @property
    def gain(self) -> dict:
        """
            Get camera current gain function | 获取相机当前增益
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "gain" : float
                }
            }
        """

    @property
    def offset(self) -> dict:
        """
            Get camera current offset function | 获取相机当前偏置
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "offset" : float
                }
            }
        """

    @property
    def binning(self) -> dict:
        """
            Get camera current binning function | 获取相机当前像素合并
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "binning" : int
                }
            }
        """

    @property
    def temperature(self) -> dict:
        """
            Get camera current temperature function | 获取相机当前温度
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "temperature" : float
                }
            }
        """

    @property
    def cooling_power(self) -> dict:
        """
            Get camera current cooling power function | 获取相机当前制冷功率
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "power" : float
                }
            }
        """

    # #################################################################
    #
    # Camera Status
    #
    # #################################################################

    @property
    def is_connected(self) -> dict:
        """
            Is camera connected | 是否连接成功
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : bool
                }
            }
        """

    @property
    def is_exposure(self) -> dict:
        """
            Is exposure function | 是否在曝光
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : int
                }
            }
        """

    @property
    def is_video(self) -> dict:
        """
            Is video function | 是否在录制视频
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : bool
                }
            }
        """

    @property
    def is_guiding(self) -> dict:
        """
            Is guiding | 是否在导星
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : bool
                }
            }
            NOTE : This function needs camera support
        """

    @property
    def is_cooling(self) -> dict:
        """
            Is camera cooling | 相机是否在制冷
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : bool
                }
            }
        """

    @property
    def is_imageready(self) -> dict:
        """
            Is imageready function | 图像处理是否完成
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : bool
                }
            }
        """

    # #################################################################
    #
    # Camera Properties
    #
    # #################################################################    

    @property
    def maxmin_gain(self) -> dict:
        """
            Get camera max and min gain function | 获取最大最小增益
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "max_gain" : float,
                    "min_gain" : float
                }
        """

    @property
    def maxmin_offset(self) -> dict:
        """
            Get the maximum and minimum offset | 获取最大最小增益
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "max_offset" : float,
                    "min_offset" : float
                }
            }
        """

    @property
    def maxmin_exposure(self) -> dict:
        """
            Get the maximum and minimum exposure | 获取曝光最长和最短时间
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "max_exposure" : float,
                    "min_exposure" : float
                }
            }
        """

    @property
    def max_bin(self) -> dict:
        """
            Get the maximum bin | 获取最大像素合并
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "max_bin" : int
                }
            }            
        """

    @property
    def frame(self) -> dict:
        """
            Get the current frame infomation | 获取画幅信息
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "height" : int, # current height of the image
                    "width" : int, # current width of the image
                    "bayer_offset_x" : int,
                    "bayer_offset_y" : int,
                    "subframe_x" : int,
                    "subframe_y" : int,
                    "start_x" : int # current start position
                    "start_y" : int # current start position
                    "pixel_height" : float,
                    "pixel_width" : float
                }
            }
        """

    @property
    def readout(self) -> dict:
        """
            Get the readout mode and info about sensor | 获取相机输出模式并且获取芯片信息
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "readout_mode" : int,
                    "sensor_type" : str,
                    "sensor_name" : str,
                }
            }
            NOTE : This function needs camera and software support
        """

    # #################################################################
    #
    # Camera Ability
    #
    # #################################################################

    @property
    def can_binning(self) -> dict:
        """
            Check if camera can binning | 是否是否支持像素合并
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : bool
                }
            }
        """

    @property
    def can_cooling(self) -> dict:
        """
            Check if camera can cooling | 相机是否支持制冷
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : bool
                }
            }
            NOTE : This function needs camera support
        """

    @property
    def can_gain(self) -> dict:
        """
            Check if camera can gain | 相机是否支持增益
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : bool
                }
            }
            NOTE : I'm not sure whether DSLR is supported
        """

    @property
    def can_get_coolpower(self) -> dict:
        """
            Check if camera can get coolpower | 相机是否支持获取制冷功率
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : bool
                }
            }
            NOTE : This function needs camera support
        """

    @property
    def can_guiding(self) -> dict:
        """
            Check if camera can guiding | 相机是否支持导星
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : bool
                }
            }
        """

    @property
    def can_has_shutter(self) -> dict:
        """
            Check if camera can has shutter | 相机是否有机械快门
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : bool
                }
            }
        """

    @property
    def can_iso(self) -> dict:
        """
            Check if camera can iso | 相机是否支持输入 ISO
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : bool
                }
            }
        """

    @property
    def can_offset(self) -> dict:
        """
            Check if camera can offset | 相机是否支持偏置
            Args : None
            Returns : {
                "status" : int,
                "message" : str,
                "params" : {
                    "status" : bool
                }
            }
            NOTE : I'm not sure whether DSLR is supported
        """