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

class AscomCameraError(Enum):
    """
        Regular ASCOM camera error
    """
    OneDevice = _("Each server can only connect to one device at a time")
    NotConnected = _("Camera is not connected")
    NetworkError = _("Network error occurred")
    DriverError = _("Driver error occurred")
    InvalidOperation = _("Invalid operation")

    NoHostValue = _("No host value provided")
    NoPortValue = _("No port value provided")
    NoDeviceNumber = _("No device number provided")
    NoExposureValue = _("No exposure value provided")
    NoGainValue = _("No gain value provided")
    NoOffsetValue = _("No offset value provided")
    NoISOValue = _("No ISO value provided")

    InvalidExposureValue = _("Invalid exposure value provided")
    InvalidGainValue = _("Invaild gain value provided , default is 20")
    InvalidOffsetValue = _("Invalid offsets value provided , default is 20")
    InvalidBinningValue = _("Invalid binding mode value provided , default is 1")

    CanNotGetTemperature = _("Could not get camera current temperature")
    CanNotGetPower = _("Could not get camera current cooling power")

    AbortExposureError = _("Abort exposure failed")

class AscomCameraSuccess(Enum):
    """
        Regular ASCOM camera success
    """

    ScanningSuccess = _("Scanning camera successfully")
    ReconnectSuccess = _("Reconnect camera successfully")
    PollingSuccess = _("Camera's information is refreshed successfully")
    GetConfigrationSuccess = _("Get camera configuration successfully")
    SaveConfigrationSuccess = _("Save camera configuration successfully")

    AbortExposureSuccess = _("Abort exposure successfully")

class AscomCameraWarning(Enum):
    """
        Regular ASCOM camera warning
    """
    DisconnectBeforeScanning = _("Please disconnect your camera before scanning")