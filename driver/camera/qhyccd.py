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
the Free Software Foundation, Inctypes., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301, USA.

"""

from driver.basiccamera import BasicCamera, CameraInfo
from utils.lightlog import lightlog
log = lightlog(__name__)

class camera(BasicCamera):
    """QHY Camera class"""

    def __init__(self) -> None:
        super().__init__()

    def __del__(self) -> None:
        return super().__del__()

        