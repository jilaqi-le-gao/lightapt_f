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

import ctypes
import os
import sys
from driver.basiccamera import BasicCamera,CameraInfo
from utils.lightlog import lightlog
log = lightlog(__name__)

import gettext
_ = gettext.gettext

# ASI_BAYER_PATTERN
ASI_BAYER_RG = 0
ASI_BAYER_BG = 1
ASI_BAYER_GR = 2
ASI_BAYER_RB = 3

# ASI_IMGTYPE
ASI_IMG_RAW8 = 0
ASI_IMG_RGB24 = 1
ASI_IMG_RAW16 = 2
ASI_IMG_Y8 = 3
ASI_IMG_END = -1

# ASI_GUIDE_DIRECTION
ASI_GUIDE_NORTH = 0
ASI_GUIDE_SOUTH = 1
ASI_GUIDE_EAST = 2
ASI_GUIDE_WEST = 3

ASI_GAIN = 0
ASI_EXPOSURE = 1
ASI_GAMMA = 2
ASI_WB_R = 3
ASI_WB_B = 4
ASI_BRIGHTNESS = 5
ASI_OFFSET = 5
ASI_BANDWIDTHOVERLOAD = 6
ASI_OVERCLOCK = 7
ASI_TEMPERATURE = 8  # return 10*temperature
ASI_FLIP = 9
ASI_AUTO_MAX_GAIN = 10
ASI_AUTO_MAX_EXP = 11
ASI_AUTO_MAX_BRIGHTNESS = 12
ASI_HARDWARE_BIN = 13
ASI_HIGH_SPEED_MODE = 14
ASI_COOLER_POWER_PERC = 15
ASI_TARGET_TEMP = 16  # not need *10
ASI_COOLER_ON = 17
ASI_MONO_BIN = 18  # lead to less grid at software bin mode for color camera
ASI_FAN_ON = 19
ASI_PATTERN_ADJUST = 20

# ASI_CAMERA_MODE
ASI_MODE_NORMAL = 0 
ASI_MODE_TRIG_SOFT_EDGE = 1
ASI_MODE_TRIG_RISE_EDGE = 2
ASI_MODE_TRIG_FALL_EDGE = 3
ASI_MODE_TRIG_SOFT_LEVEL = 4
ASI_MODE_TRIG_HIGH_LEVEL = 5
ASI_MODE_TRIG_LOW_LEVEL = 6
ASI_MODE_END = -1

# ASI_TRIG_OUTPUT
ASI_TRIG_OUTPUT_PINA = 0
ASI_TRIG_OUTPUT_PINB = 1
ASI_TRIG_OUTPUT_NONE = -1

# ASI_EXPOSURE_STATUS
ASI_EXP_IDLE = 0
ASI_EXP_WORKING = 1
ASI_EXP_SUCCESS = 2
ASI_EXP_FAILED = 3

class ZWO_Error(Exception):
    """Exception class for errors returned from the :mod:`zwoasi` module."""
    def __init__(self, message):
        Exception.__init__(self, message)


class ZWO_IOError(ZWO_Error):
    """Exception class for all errors returned from the ASI SDK library."""
    def __init__(self, message, error_code=None):
        ZWO_Error.__init__(self, message)
        self.error_code = error_code

class ZWO_CaptureError(ZWO_Error):
    """Exception class for when :func:`Camera.capture()` fails."""
    def __init__(self, message, exposure_status=None):
        ZWO_Error.__init__(self, message)
        self.exposure_status = exposure_status
        
# Mapping of error numbers to exceptions. Zero is used for success.
zwo_errors = [None,
              ZWO_IOError('Invalid index', 1),
              ZWO_IOError('Invalid ID', 2),
              ZWO_IOError('Invalid control type', 3),
              ZWO_IOError('Camera closed', 4),
              ZWO_IOError('Camera removed', 5),
              ZWO_IOError('Invalid path', 6),
              ZWO_IOError('Invalid file format', 7),
              ZWO_IOError('Invalid size', 8),
              ZWO_IOError('Invalid image type', 9),
              ZWO_IOError('Outside of boundary', 10),
              ZWO_IOError('Timeout', 11),
              ZWO_IOError('Invalid sequence', 12),
              ZWO_IOError('Buffer too small', 13),
              ZWO_IOError('Video mode active', 14),
              ZWO_IOError('Exposure in progress', 15),
              ZWO_IOError('General error', 16),
              ZWO_IOError('Invalid mode', 17)
              ]

class _ASI_CAMERA_INFO(ctypes.Structure):
    """ASI camera info"""
    _fields_ = [
        ('Name', ctypes.c_char * 64),
        ('CameraID', ctypes.c_int),
        ('MaxHeight', ctypes.c_long),
        ('MaxWidth', ctypes.c_long),
        ('IsColorCam', ctypes.c_int),
        ('BayerPattern', ctypes.c_int),
        ('SupportedBins', ctypes.c_int * 16),
        ('SupportedVideoFormat', ctypes.c_int * 8),
        ('PixelSize', ctypes.c_double),  # in um
        ('MechanicalShutter', ctypes.c_int),
        ('ST4Port', ctypes.c_int),
        ('IsCoolerCam', ctypes.c_int),
        ('IsUSB3Host', ctypes.c_int),
        ('IsUSB3Camera', ctypes.c_int),
        ('ElecPerADU', ctypes.c_float),
        ('BitDepth', ctypes.c_int),
        ('IsTriggerCam', ctypes.c_int),

        ('Unused', ctypes.c_char * 16)
    ]
    
    def get_dict(self) -> dict:
        r = {}
        for k, _ in self._fields_:
            v = getattr(self, k)
            if sys.version_info[0] >= 3 and isinstance(v, bytes):
                v = v.decode()
            r[k] = v
        del r['Unused']
        
        r['SupportedBins'] = []
        for i in range(len(self.SupportedBins)):
            if self.SupportedBins[i]:
                r['SupportedBins'].append(self.SupportedBins[i])
            else:
                break
        r['SupportedVideoFormat'] = []
        for i in range(len(self.SupportedVideoFormat)):
            if self.SupportedVideoFormat[i] is ASI_IMG_END:
                break
            r['SupportedVideoFormat'].append(self.SupportedVideoFormat[i])

        for k in ('IsColorCam', 'MechanicalShutter', 'IsCoolerCam',
                  'IsUSB3Host', 'IsUSB3Camera'):
            r[k] = bool(getattr(self, k))
        return r


class _ASI_CONTROL_CAPS(ctypes.Structure):
    _fields_ = [
        ('Name', ctypes.c_char * 64),
        ('Description', ctypes.c_char * 128),
        ('MaxValue', ctypes.c_long),
        ('MinValue', ctypes.c_long),
        ('DefaultValue', ctypes.c_long),
        ('IsAutoSupported', ctypes.c_int),
        ('IsWritable', ctypes.c_int),
        ('ControlType', ctypes.c_int),
        ('Unused', ctypes.c_char * 32),
        ]

    def get_dict(self) -> dict:
        r = {}
        for k, _ in self._fields_:
            v = getattr(self, k)
            if sys.version_info[0] >= 3 and isinstance(v, bytes):
                v = v.decode()
            r[k] = v
        del r['Unused']
        for k in ('IsAutoSupported', 'IsWritable'):
            r[k] = bool(getattr(self, k))
        return r


class _ASI_ID(ctypes.Structure):
    _fields_ = [('id', ctypes.c_char * 8)]

    def get_id(self) -> dict:
        # return self.id
        v = self.id
        if sys.version_info[0] >= 3 and isinstance(v, bytes):
            v = v.decode()
        return v


class _ASI_SUPPORTED_MODE(ctypes.Structure):
    _fields_ = [('SupportedCameraMode', ctypes.c_int * 16)]

    def get_dict(self)  -> dict:
        base_dict = {k: getattr(self, k) for k, _ in self._fields_}
        base_dict['SupportedCameraMode'] = [int(x) for x in base_dict['SupportedCameraMode']]

class camera(BasicCamera):
    """ASI Camera class"""

    def __init__(self) -> None:
        self.info = CameraInfo()
        self.device = None
        self.zwolib = None
        log.log(_("Initlize ASI Camera object successfully"))

    def __del__(self) -> None:
        """Delete camera object"""
        if self.info._is_connected:
            if self.disconnect({}).get("status") != "success":
                log.loge(_("Failed to disconnect from ASI camera"))
                return
        self.device = None
        log.log(_("Delete ASI camera object successfully"))

    def connect(self, params: dict) -> dict:
        """
            Connect to camera | 连接相机
            Args:
                {
                    "name" : str # Name of camera
                    "count" : int # Number of cameras
                }
            Return:
                {
                    "status" : "success","error","warning","debug"
                    "message" : str
                    "params" : {
                        "info" : CameraInfo object
                        "name" : Name of camera
                    }
                }
            NOTE : This must be called and run successfully before continuing operation
        """

    def init(self) -> None:
        """
            Initlize ASI resourse and dll library | 初始化ASI相机
            Args : None
            Return : {
                "status" : "success","error","warning","debug",
                "message" : str
                "params" : {

                }
            }
            NOTE : This is only for ASI camera , do not use it with other camera
        """
        if self.zwolib is not None:
            return
        _p = os.path.join
        libpath = _p(_p(os.getcwd(),"lib"),"zwoasi")
        # 判断系统位数 - 32/64
        if 'PROGRAMFILES(X86)' in os.environ:
            libpath = _p(_p(libpath,"x64"),"ASICamera2.dll")
        else:
            libpath = _p(_p(libpath,"x86"),"ASICamera2.dll")
        # 检查库是否存在
        if os.path.isfile(libpath):
            log.log(f"Find {libpath}")
        else:
            log.loge(f"Failed to find {libpath}")
        # 加载动态库
        """Initlize camera driver library"""
        self.zwolib = ctypes.cdll.LoadLibrary(libpath)
        """Get the number of cameras | 获取相机数量"""
        self.zwolib.ASIGetNumOfConnectedCameras.argtypes = []
        self.zwolib.ASIGetNumOfConnectedCameras.restype = ctypes.c_int
        """Get property of cameras | 获取相机配置"""
        self.zwolib.ASIGetCameraProperty.argtypes = [ctypes.POINTER(_ASI_CAMERA_INFO), ctypes.c_int]
        self.zwolib.ASIGetCameraProperty.restype = ctypes.c_int
        """Open camera | 打开相机"""
        self.zwolib.ASIOpenCamera.argtypes = [ctypes.c_int]
        self.zwolib.ASIOpenCamera.restype = ctypes.c_int
        """Initial camera | 初始化相机"""
        self.zwolib.ASIInitCamera.argtypes = [ctypes.c_int]
        self.zwolib.ASIInitCamera.restype = ctypes.c_int
        """Close camera | 关闭相机"""
        self.zwolib.ASICloseCamera.argtypes = [ctypes.c_int]
        self.zwolib.ASICloseCamera.restype = ctypes.c_int
        """Get the number of cameras' control types | 获取相机控制类型的数量"""
        self.zwolib.ASIGetNumOfControls.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.zwolib.ASIGetNumOfControls.restype = ctypes.c_int

        self.zwolib.ASIGetControlCaps.argtypes = [ctypes.c_int, ctypes.c_int,
                                            ctypes.POINTER(_ASI_CONTROL_CAPS)]
        self.zwolib.ASIGetControlCaps.restype = ctypes.c_int

        self.zwolib.ASIGetControlValue.argtypes = [ctypes.c_int,
                                            ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_long),
                                            ctypes.POINTER(ctypes.c_int)]
        self.zwolib.ASIGetControlValue.restype = ctypes.c_int

        self.zwolib.ASISetControlValue.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_long, ctypes.c_int]
        self.zwolib.ASISetControlValue.restype = ctypes.c_int

        self.zwolib.ASIGetROIFormat.argtypes = [ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_int),
                                        ctypes.POINTER(ctypes.c_int),
                                        ctypes.POINTER(ctypes.c_int),
                                        ctypes.POINTER(ctypes.c_int)]
        self.zwolib.ASIGetROIFormat.restype = ctypes.c_int

        self.zwolib.ASISetROIFormat.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.zwolib.ASISetROIFormat.restype = ctypes.c_int

        self.zwolib.ASIGetStartPos.argtypes = [ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_int),
                                        ctypes.POINTER(ctypes.c_int)]
        self.zwolib.ASIGetStartPos.restype = ctypes.c_int

        self.zwolib.ASISetStartPos.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.zwolib.ASISetStartPos.restype = ctypes.c_int

        self.zwolib.ASIGetDroppedFrames.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.zwolib.ASIGetDroppedFrames.restype = ctypes.c_int

        self.zwolib.ASIEnableDarkSubtract.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_char)]
        self.zwolib.ASIEnableDarkSubtract.restype = ctypes.c_int

        self.zwolib.ASIDisableDarkSubtract.argtypes = [ctypes.c_int]
        self.zwolib.ASIDisableDarkSubtract.restype = ctypes.c_int

        self.zwolib.ASIStartVideoCapture.argtypes = [ctypes.c_int]
        self.zwolib.ASIStartVideoCapture.restype = ctypes.c_int

        self.zwolib.ASIStopVideoCapture.argtypes = [ctypes.c_int]
        self.zwolib.ASIStopVideoCapture.restype = ctypes.c_int

        self.zwolib.ASIGetVideoData.argtypes = [ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_char),
                                        ctypes.c_long,
                                        ctypes.c_int]
        self.zwolib.ASIGetVideoData.restype = ctypes.c_int

        self.zwolib.ASIPulseGuideOn.argtypes = [ctypes.c_int, ctypes.c_int]
        self.zwolib.ASIPulseGuideOn.restype = ctypes.c_int

        self.zwolib.ASIPulseGuideOff.argtypes = [ctypes.c_int, ctypes.c_int]
        self.zwolib.ASIPulseGuideOff.restype = ctypes.c_int

        self.zwolib.ASIStartExposure.argtypes = [ctypes.c_int, ctypes.c_int]
        self.zwolib.ASIStartExposure.restype = ctypes.c_int

        self.zwolib.ASIStopExposure.argtypes = [ctypes.c_int]
        self.zwolib.ASIStopExposure.restype = ctypes.c_int

        self.zwolib.ASIGetExpStatus.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.zwolib.ASIGetExpStatus.restype = ctypes.c_int

        self.zwolib.ASIGetDataAfterExp.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_char), ctypes.c_long]
        self.zwolib.ASIGetDataAfterExp.restype = ctypes.c_int

        self.zwolib.ASIGetID.argtypes = [ctypes.c_int, ctypes.POINTER(_ASI_ID)]
        self.zwolib.ASIGetID.restype = ctypes.c_int

        self.zwolib.ASISetID.argtypes = [ctypes.c_int, _ASI_ID]
        self.zwolib.ASISetID.restype = ctypes.c_int


        self.zwolib.ASIGetGainOffset.argtypes = [ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int),
                                            ctypes.POINTER(ctypes.c_int)]
        self.zwolib.ASIGetGainOffset.restype = ctypes.c_int

        self.zwolib.ASISetCameraMode.argtypes = [ctypes.c_int, ctypes.c_int]
        self.zwolib.ASISetCameraMode.restype = ctypes.c_int

        self.zwolib.ASIGetCameraMode.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.zwolib.ASIGetCameraMode.restype = ctypes.c_int

        self.zwolib.ASIGetCameraSupportMode.argtypes = [ctypes.c_int, ctypes.POINTER(_ASI_SUPPORTED_MODE)]
        self.zwolib.ASIGetCameraSupportMode.restype = ctypes.c_int

        self.zwolib.ASISendSoftTrigger.argtypes = [ctypes.c_int, ctypes.c_int]
        self.zwolib.ASISendSoftTrigger.restype = ctypes.c_int

        self.zwolib.ASISetTriggerOutputIOConf.argtypes = [ctypes.c_int,
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ctypes.c_long,
                                                    ctypes.c_long]
        self.zwolib.ASISetTriggerOutputIOConf.restype = ctypes.c_int

        self.zwolib.ASIGetTriggerOutputIOConf.argtypes = [ctypes.c_int,
                                                    ctypes.c_int,
                                                    ctypes.POINTER(ctypes.c_int),
                                                    ctypes.POINTER(ctypes.c_long),
                                                    ctypes.POINTER(ctypes.c_long)]
        self.zwolib.ASIGetTriggerOutputIOConf.restype = ctypes.c_int

        self.zwolib.ASIGetSDKVersion.restype = ctypes.c_char_p

        log.log(f"Processing ASILib completed")
