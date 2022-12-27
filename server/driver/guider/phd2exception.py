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

from enum import Enum

from gettext import gettext
_ = gettext

class PHD2Success(Enum):
    """
        Regular PHD2 operation success
    """
    Send = _("Send command to PHD2 server successfully")
    Paused = _("Guiding is paused")
    StartLooping = _("Start looping exposure successfully")
    SetAlgoParam = _("Set algo parameter successfully")
    SetConnected = _("Set connected parameter successfully")
    SetDECGuideMode = _("Set DEC guide mode successfully")
    SetGuideOutputEnabled = _("Set guide output enabled successfully")
    SetLockPosition = _("Set lock position successfully")
    SetLockShiftEnabled = _("Set lock shift enabled successfully")
    SetPaused = _("Set paused successfully")
    SetProfile = _("Set profile successfully")
    Shutdown = _("Shutdown server successfully")

    SendGetUseSubframe = _("Sent get use subframes command to PHD2 server successfully")
    SendGuide = _("Sent guide command to PHD2 server successfully")
    SendPulse = _("Sent pulse command to PHD2 server successfully")
    SendLooping = _("Sent looping command to PHD2 server successfully")
    SendSaveImage = _("Sent save image command to PHD2 server successfully")
    SendSetAlgoParam = _("Sent set algo parameter to PHD2 server successfully")
    SendSetConnected = _("Sent set connected command to PHD2 server successfully")
    SendSetDECGuideMode = _("Sent set dec guide mode to PHD2 server parameter successfully")
    SendSetExposure = _("Sent set exposure parameter to PHD2 server successfully")
    SendSetGuideOutputEnabled = _("Sent set guide output enabled parameter to PHD2 server successfully")
    SendSetLockPosition = _("Sent set lock position parameter to PHD2 server successfully")
    SendSetLockShiftEnabled = _("Sent set lock shift enabled parameter to PHD2 server successfully")
    SendSetPaused = _("Sent set paused to PHD2 server successfully")
    SendSetProfile = _("Sent set profile to PHD2 server successfully")

class PHD2Error(Enum):
    """
        Regular PHD2 operation error
    """

    InvalidDECGuideMode = _("Invalid DEC guide mode")
    InvalidExposureValue = _("Invalid Exposure value")
    InvalidEnableValue = _("Invalid enable value")
    InvalidLockPositionValue = _("Invalid Lock position value")
    InvalidPausedFullValue = _("Invalid paused and full value")
    InvalidProfileID = _("Invalid Profile ID")

    NotConnected = _("PHD2 server is not connected")

    SendFailed = _("Failed to send command to PHD2 server")
    SendGetUseSubframeFailed = _("Failed to send get use subframes command to PHD2 server")
    SendGuideFailed = _("Failed to send guide command to PHD2 server")
    SendPulseFailed = _("Failed to send pulse command to PHD2 server")
    SendLoopingFailed = _("Failed to send looping command to PHD2 server")
    SendSaveImageFailed = _("Failed to send save image command to PHD2 server")
    SendSetAlgoParamFailed = _("Failed to send set algo parameter to PHD2 server")
    SendSetConnectedFailed = _("Failed to send set connected command to PHD2 server")
    SendSetDECGuideModeFailed = _("Failed to send set DEC guide parameter command to PHD2 server")
    SendSetExposureFailed = _("Failed to send set EXposure parameter command to PHD2 server")
    SendSetGuideOutputEnabledFailed = _("Failed to send set guide output enabled parameter command to PHD2 server")
    SendSetLockPositionFailed = _("Failed to send set lock position command to PHD2 server")
    SendSetLockShiftEnabledFailed = _("Failed to send set lock shift parameter command to PHD2 server")
    SendSetPausedFailed = _("Failed to send set paused command to PHD2 server")
    SendSetProfileFailed = _("Failed to send set profile command to PHD2 server")

    DisconnectFailed = _("Failed to disconnect from PHD2 server")
    StartLoopingFailed = _("Failed to start looping exposure")
    StartGuidingFailed = _("Failed to start guiding")
    SetConnectedFailed = _("Failed to device connection status")
    SetDECGuideModeFailed = _("Failed to set DEC guide mode")
    SetGuideOutputEnabledFailed = _("Failed to set guide output enabled")
    SetLockPositionFailed = _("Failed to set a lock position")
    SetLockShiftEnabledFailed = _("Failed to set a lock shift enabled")
    SetPausedFailed = _("Failed to set paused")
    SetProfileFailed = _("Failed to set profile")
    ShutdownFailed = _("Failed to shut down server")
    
    PulseGuidingFailed = _("Failed to pulse guide process")

class PHD2Warning(Enum):
    """
        Regular PHD2 operation warning
    """
    GuidingAlreadyStarted = _("PHD2 server is already started guiding")
    DeviceAlreadyConnected = _("Device already connected , please do not connect again")
    IsCalibrating = _("PHD2 server is calibrating now, please wait for a moment")