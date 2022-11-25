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
__all__ = ["log", "loge", "logw" ,"logd"]

import logging
from colorama import Fore,init
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

init(autoreset=True)
sleep(0.5)

DEBUG = False

class lightlog():
    """
        Light weight log system for LightAPT
        Initial : log = lightlog(__name__)
        Mode : "info","warning","error","debug"
        Return : None (All logger functions)
        Note: Nearly every file needs to include this
    """

    def __init__(self,name : str) -> None:
        """Initialize logger"""
        self.uname = name
        
    #日志
    def log(self,msg : str) -> None:
        """
            Log normal message | 普通信息日志\n
            Args:
                msg: str # can be format string
            Return: None
        """
        if self._check_(msg):
            logger.info(f"[{self.uname}][INFO] - {msg}")
        else:
            logger.error(_("Invalid message type"))

    # 错误日志
    def loge(self,msg : str) -> None:
        """
            Log error message | 错误信息日志\n
            Args:
                msg: str # can be format string
            Return: None
        """
        if self._check_(msg):
            logger.info(f"[{self.uname}][ERROR] - " + Fore.RED + f"{msg}" + Fore.RESET)
        else:
            logger.error(_("Invalid message type"))

    # 警告日志
    def logw(self,msg : str) -> None:
        """
            Log warning message | 警告信息日志\n
            Args:
                msg: str # can be format string
            Return: None
        """
        if self._check_(msg):
            logger.info(f"[{self.uname}][WARNING] - " + Fore.YELLOW + f"{msg}" + Fore.RESET)
        else:
            logger.error(_("Invalid message type"))
        

    # 调试日志
    def logd(self,msg) -> None:
        """
            Log debug message | 调试日志\n
            Args:
                msg: str # can be format string
            Return: None
        """
        if DEBUG:
            if self._check_(msg):
                logger.info(f"[{self.uname}][DEBUG] - " + Fore.MAGENTA + f"{msg}" + Fore.RESET)
            else:
                logger.error(_("Invalid message type"))
        

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