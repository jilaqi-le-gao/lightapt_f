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

__version__ = "1.0.0"
__author__ = "Max Qian"
__license__ = "GPL3"
__class__ = "lightlog"

import logging
from os import mkdir, path
from time import sleep, strftime

import gettext
_ = gettext.gettext

# Initialize logger object | 初始化日志对象 
logger = logging.getLogger(__name__)
fort = logging.Formatter('[%(asctime)s]%(message)s')
# logger parameters | 控制台日志参数
console_handle = logging.StreamHandler()
console_handle.setFormatter(fort)
logger.addHandler(console_handle)
# Output log into a file | 文件日志
if not path.exists("./logs"):
    mkdir("./logs")
file_handle = logging.FileHandler(filename=f"logs/{strftime('%Y-%m-%d#%H%M%S')}.log",encoding="utf-8",mode="w+")
file_handle.setFormatter(fort)
logger.addHandler(file_handle)
# Set logger level | 设置日志级别
logger.setLevel(logging.INFO)

DEBUG = True

class lightlog():
    """
        Light weight log system for LightAPT
        Initial : log = lightlog(__name__)
        NOTE : Every file should include this.
    """

    def __init__(self,name : str) -> None:
        """Initialize logger"""
        self.uname = name

    def log(self,msg : str) -> None:
        """
            Log normal message | 普通信息日志\n
            Args:
                msg: str # can be format string
            Return: None
        """
        if self._check_(msg):
            logger.info(f"[{self.uname}][INFO] - {msg}")

    def loge(self,msg : str) -> None:
        """
            Log error message | 错误信息日志\n
            Args:
                msg: str # can be format string
            Return: None
        """
        if self._check_(msg):
            logger.info(f"[{self.uname}][ERROR] - "+ f"{msg}")

    def logw(self,msg : str) -> None:
        """
            Log warning message | 警告信息日志\n
            Args:
                msg: str # can be format string
            Return: None
        """
        if self._check_(msg):
            logger.info(f"[{self.uname}][WARNING] - " + f"{msg}")
        
    def logd(self,msg) -> None:
        """
            Log debug message | 调试日志\n
            Args:
                msg: str # can be format string
            Return: None
        """
        if DEBUG and self._check_(msg):
            logger.info(f"[{self.uname}][DEBUG] - " + f"{msg}")

    def _check_(self,msg) -> bool:
        """
            Check if the message is a valid
            Args:
                msg : str
            Return:
                bool: True if the message is correct, False otherwise
        """
        if not isinstance(msg,str):
            return False
        return True

    def return_success(self,info : str , params = {}) -> dict:
        """
            Return success message | 返回信息
            Args :
                info : str
                params : dict
            Returns : dict
        """
        return {
            "status" : 0,
            "message" : info if info is not None else None,
            "params" :  params if params is not None else {}
        }

    def return_error(self,info : str,params = {}) -> dict :
        """
            Return error message | 返回错误
            Args:
                info: str # Info message
                params : dict # Container
            Return : dict
        """
        return {
            "status" : 1,
            "message" : info if info is not None else None,
            "params" : params if params is not None else {} 
        }

    def return_warning(self,info : str,params = {}) -> dict:
        """
            Return warning message | 返回警告
            Args:
                info: str # Info message
                params : dict # Container
            Return : dict
        """
        return {
            "status" : 2,
            "message" : info if info is not None else None,
            "params" : params if params is not None else {}
        }

class new_lightlog():
    """
        Light weight log system for LightAPT to replace the old logging module
        Initial : logger = new_lightlog(__name__)
        NOTE : Every file should include this.
    """

    def __init__(self,name : str) -> None:
        """
            Initialize a new lightlog object
            Args:
                name : str
            Returns:
        """
        self.uname = name

    def info(self,msg : str) -> None:
        """
            Log normal message | 普通信息日志\n
            Args:
                msg: str # can be format string
            Return: None
        """
        logger.info(f"[{self.uname}][INFO] - {msg}")

    def error(self,msg : str) -> None:
        """
            Log error message | 错误信息日志\n
            Args:
                msg: str # can be format string
            Return: None
        """
        logger.info(f"[{self.uname}][ERROR] - "+ f"{msg}")

    def warning(self,msg : str) -> None:
        """
            Log warning message | 警告信息日志\n
            Args:
                msg: str # can be format string
            Return: None
        """
        logger.info(f"[{self.uname}][WARNING] - " + f"{msg}")
        
    def debug(self,msg) -> None:
        """
            Log debug message | 调试日志\n
            Args:
                msg: str # can be format string
            Return: None
        """
        if DEBUG:
            logger.info(f"[{self.uname}][DEBUG] - " + f"{msg}")