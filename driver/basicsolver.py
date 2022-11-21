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

import os
from yaml import safe_load,safe_dump
import astropy.io.fits as fits
from astropy.utils.data import get_pkg_data_filename
from core.lib.starlog import starlog

log = starlog(__name__)

import gettext
_ = gettext.gettext

__api__ = "Solver Basic API"
__api_version__ = "1.0.0"
__copyright__ = "Max Qian"
__license__ = "GPL3"

class SolverInfo(object):
    """Solver information"""

    def get_dict(self) -> dict:
        """Return a dictionary which contains the information about the solver"""


class BasicSolver(object):
    """Basic solver class"""

    def __init__(self) -> None:
        """Initialize the solver"""

    def __del__(self) -> None:
        """Delete the solver"""

    def return_message(self,status : str, message : str ,params = {}) -> dict:
        """
            Return the message in dict format | 以字典的形式返回结果
            :param status:
            :param message:
            :param params:
            :return: {
                "status": str,
                "message": str,
                "params": dict
            }
        """
        return {
            "status" : status,
            "message" : message,
            "params" : params
        }

    def load_config(self,params : dict) -> dict:
        """
            Load the config file
            :param params:
            :return: {
                "status": str,
                "message": str,
                "params": dict
            }
        """
        return params

    def save_config(self) -> dict:
        """
            Save the configuration file | 保存配置文件
            Return:
                {
                    "status" : "success","error","warning","debug"
                    "message" : str
                    "params" : {
                        "error" : exception
                    }
                }
        """
        _p = os.path.join
        if self.info._config_file.find("yaml") == -1:
            self.info._config_file += ".yaml"
        folder = _p("config",_p("device","dome"))
        if not os.path.exists(folder):
            os.mkdir(folder)
        path = _p(_p(_p(_p(os.getcwd(),"config"),"device"),"dome"),self.info._config_file)
        if os.path.isfile(path):
            """TODO"""
        try:
            with open(path,mode="w+",encoding="utf-8") as file:
                safe_dump(self.info.get_dict(), file)
        except IOError as exception:
            log.loge(_(f"Faild to save configuration file {path} error : {exception}"))
            return self.return_message("error", _("Faild to save configuration file %(path)"),self.info.get_dict())
        log.log(_("Save configuration file successfully"))
        return self.return_message("success", _("Save configuration file successfully"),self.info.get_dict())

    # #################################################################
    # Online solver
    # #################################################################

    def online_solver(self,params : dict) -> dict:
        """
            Online solver
            Args:
                params (dict): solver parameters
                    {
                        "filename": str
                        "path": str
                        "url": str
                    }
            Return:
                {
                    "status" :"success","error","warning","debug"
                    "message" : str
                    "params" : {
                        "info": 
                    }
                }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"),{})

    def upload_image(self,params : dict) -> dict:
        """
            Upload image
            Args:
                params (dict): solver parameters
                    {
                        "filename": str
                        "path": str
                        "url": str
                    }
            Return:
                {
                    "status" :"success","error","warning","debug"
                    "message" : str
                    "params" : {
                        "info": 
                    }
                }
        """
        log.loge("The parent function should not be called")
        return self.return_message("error",_("The parent function should not be called"),{})


    # #############################################################
    # Offline solver
    # #############################################################

    def offline_solver(self,params : dict) -> dict:
        """
            Offline solver
            Args:
                params (dict): solver parameters
                    {
                        "filename": str
                        "path": str
                    }
            Return:
                {
                    "status" :"success","error","warning","debug"
                    "message" : str
                    "params" : {
                        "info": 
                    }
                }
        """
        log.loge(_("The parent function should not be called"))
        return self.return_message("error",_("The parent function should not be called"),{})

    # #############################################################
    # Image Useful Functions
    # #############################################################

    def load_image(self,params : dict) -> dict:
        """
            Load image
            Args:
                params (dict): solver parameters
                    {
                        "filename": str
                        "path": str
                    }
            Return:
                {
                    "status" :"success","error","warning","debug"
                    "message" : str
                    "params" : {
                        "data" : nparray 
                    }
                }
        """
        _p = os.path.join
        if not isinstance(params.get("filename"),str) or params.get("filename").split(".")[-1].lower() != "fits":
            log.loge(_("Invalid filename"))
            return self.return_message("error",_("Invalid filename"),{})
        path = _p(params.get("path"),params.get("filename"))
        if not os.path.exists(path):
            log.loge(_(f"Image file not found in {params.get('path')}"))
            return self.return_message("error",_("Image file not found in %(path)s"),{})
        try:
            # Preload image from filesystem | 预加载图片
            img = get_pkg_data_filename()
            # Print image information | 打印图像信息
            fits.info(img)
            # Get image data | 获取图像数据 | numpy.nparray |
            data = fits.getdata()
        except OSError as exception:
            log.loge(_(f"Faild to get image data , error : {exception}"))
            return self.return_message("error",_("Faild to get image data"),{})
        except IndexError as exception:
            log.loge(_(f"Faild to get image data index, error : {exception}"))
            return self.return_message("error",_("Faild to get image data index"),{})
        log.log(_("Load image data successfully"))
        return self.return_message("success",_("Load image data successfully"),{"data":data})


        