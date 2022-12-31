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

from utils.lightlog import lightlog
log = lightlog(__name__)

from utils.i18n import _
from re import match,split
from subprocess import check_output

class Device:
    """A collection of device"""

    def __init__(self , host = "127.0.0.1" , port = 7624):
        self.host = host
        self.port = port

    @staticmethod
    def get_devices_linux():
        """
            Get devices properties on Linux which had already install indi
        """
        cmd = ['indi_getprop', '*.CONNECTION.CONNECT']
        try:
            output = check_output(cmd).decode('utf_8')
            lines = split(r'[\n=]', output)
            output = {lines[i]: lines[i + 1] for i in range(0, len(lines) - 1, 2)}
            devices = []
            for key, val in output.items():
                device_name = match("[^.]*", key)
                devices.append({"device": device_name.group(), "connected": val == "On"})
            return devices
        except Exception as e:
            log.loge(_("Error occurred while getting devices property , error: %s") % e)

    @staticmethod
    def get_devices_windows():
        """
            Get devices properties on Windows
        """