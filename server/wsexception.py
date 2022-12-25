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

class WSCameraError(Enum):
    """
        Regular websocket camera error
    """
    ConnectError = _("Failed to connect to the camera")
    CoolingError = _("Failed to set the cooling temperature and power")

    NotSupportCooling = _("")
    NotSupportTemperatureControl = _("Camera does not support temperature control")

class WSCameraSuccess(Enum):
    """
        Regular websocket camera success
    """
    ConnectSuccess = _("Connected to the camera successfully")
    CoolingSuccess = _("Set cooling temperature and power successfully")

class WSCameraWarning(Enum):
    """
        Regular websocket camera warning
    """