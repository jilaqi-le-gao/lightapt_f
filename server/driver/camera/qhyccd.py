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

from server.basic.camera import BasicCameraAPI,BasicCameraInfo

from utils.utility import switch
from utils.lightlog import lightlog
log = lightlog(__name__)

import gettext
_ = gettext.gettext

import ctypes
import numpy as np
import astropy.io.fits as fits
from enum import Enum
from base64 import b64encode
from datetime import datetime
from io import BytesIO
from json import dumps
from os import mkdir,path,environ,getcwd
from time import sleep