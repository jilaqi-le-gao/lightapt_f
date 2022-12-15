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

class BasicCameraAPI(BasicDeviceAPI):

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

    # #################################################################
    #
    # Camera Properties
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

    @property.setter
    def gain(self, params : dict) -> dict:
        """
            Set the gain of the camera | 设置相机增益
            Args :
                "params" : {
                    "gain" : float
                }
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
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

    @property.setter
    def offset(self, params : dict) -> dict:
        """
            Set the offset of the camera | 设置相机偏置
            Args :
                "params" : {
                    "offset" : float
                }
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
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

    @property.setter
    def binning(self, params : dict) -> dict:
        """
            Set the binning of the current camera | 设置像素合并
            Args :
                "params" : {
                    "binning" : int
                }
            Returns : {
                "status" : int,
                "message" : str,
                "params" : None
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
                "status" : bool,
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
                "status" : bool,
                "message" : str,
                "params" : {
                    "status" : bool
                }
            }
        """

    @property
    def is_video(self) -> dict:
        """
            Is video function | 是否在录制视频
            Args : None
            Returns : {
                "status" : bool,
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
                "status" : bool,
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
                "status" : bool,
                "message" : str,
                "params" : {
                    "status" : bool
                }
            }
        """
