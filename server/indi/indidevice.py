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

import re
from subprocess import check_output

from utils.lightlog import lightlog
log = lightlog(__name__)

class Device:
    """A collection of device"""

    def __init__(self):
        """
            Initialize the device object
        """
        self.host = "localhost"
        self.port = 7624

    @staticmethod
    def get_devices() -> list:
        """
            Get a list of devices
            Args: None
            Returns:
                list: A list of devices
        """
        cmd = ['indi_getprop', '*.CONNECTION.CONNECT']
        try:
            output = check_output(cmd).decode('utf_8')
            lines = re.split(r'[\n=]', output)
            output = {lines[i]: lines[i + 1] for i in range(0, len(lines) - 1, 2)}
            devices = []
            for key, val in output.items():
                device_name = re.match("[^.]*", key)
                devices.append({"device": device_name.group(), "connected": val == "On"})
            return devices
        except Exception as e:
            log.loge(e)
