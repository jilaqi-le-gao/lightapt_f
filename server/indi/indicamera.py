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

from os import path,mkdir,getcwd
from json import dumps,JSONDecodeError

from server.indi.indidevice import INDIDevice
from server.basic.camera import BasicCameraAPI,BasicCameraInfo

from server.indi.indiexception import INDICameraSuccess as success
from server.indi.indiexception import INDICameraError as error
from server.indi.indiexception import INDICameraWarning as warning

class INDICamera(BasicCameraAPI,INDIDevice):
    """
        INDI Camera interface
        NOTE : If the parameters in return is None , that didn't mean that there is truly nothing.
                All error messages will be returned in "params"
    """

    def __init__(self , indi_client) -> None:
        """
            Initialize a new INDI camera object\n
            Args : 
                indi_client : INDIClient object
            Returns : None
            NOTE : I think all INDI devices should use the same INDI client
        """
        INDIDevice.__init__(self,indi_client)
        self.info = BasicCameraInfo()

    def __del__(self) -> None:
        """
            Destructor of the INDI camera object\n
            Args : None
            Returns : None
        """
        if self.info._is_connected:
            self.disconnect()

    # #########################################################################
    # Device functions
    # #########################################################################

    def connect(self, params: dict) -> dict:
        """
            Connect to a INDI camera | 连接INDI相机\n
            Args : 
                params : {
                    "name" : str # name of the camera
                }
            Returns : {
                "status" : int # status of the connection
                "message" : str # message of the connection
                "params" : {
                    "info" : BasicCameraInfo object
                }
            }
        """

    def disconnect(self) -> dict:
        """
            Disconnect from a INDI camera | 与INDI相机断开连接\n
            Args : None
            Returns : {
                "status" : int # status of the disconnection
                "message" : str # message of the disconnection
                "params" : None
            }
        """

    def reconnect(self) -> dict:
        """
            Reconnect to a INDI camera | 重连INDI相机\n
            Args : None
            Returns : {
                "status" : int # status of the reconnection
                "message" : str # message of the reconnection
                "params" : {
                    "info" : BasicCameraInfo object
                }
            }
            NOTE : This function just like a encapsulation of "connect" and "disconnect"
        """

    def scanning(self) -> dict:
        """
            Scan all of the INDI camera in certain INDI server | 扫描INDI相机在已经确定的INDI服务端\n
            Args : None
            Returns : {
                "status" : int # status of the scanning
                "message" : str # message of the scanning
                "params" : {
                    "list" : a list of camera been found
                }
            }
            NOTE : We suggest you to call this function before connect
        """

    def polling(self) -> dict:
        """
            Polling the new information of the connected camera
            Args : None
            Returns : {
                "status" : int # status of the polling
                "message" : str # message of the polling
                "params" : {
                    "info" : BasicCameraInfo object
                }
            }
            NOTE : This function is just return the self.info
        """

    def get_configration(self) -> dict:
        """
            Get the configuration of the connected camera
            Args : None
            Returns : {
                "status" : int 
                "message" : str 
                "params" : {
                    "info" : BasicCameraInfo object
                }
            }
        """

    def set_configration(self, params: dict) -> dict:
        return super().set_configration(params)

    def load_configration(self) -> dict:
        return super().load_configration()

    def save_configration(self) -> dict:
        """
            Save configration of camera
            Args : None
            Return : {
                "status" : int,
                "message" : str,
                "params" : None
            }
        """
        _p = path.join
        _path = _p(getcwd() , "config","camera",self.info._name+".json")
        if not path.exists("config"):
            mkdir("config")
        if not path.exists(_p("config","camera")):
            mkdir(_p("config","camera"))
        self.info._configration = _path
        try:
            with open(_path,mode="w+",encoding="utf-8") as file:
                try:
                    file.write(dumps(self.info.get_dict(),indent=4,ensure_ascii=False))
                except JSONDecodeError as e:
                    log.loge(_(f"JSON decoder error , error : {e}"))
        except OSError as e:
            log.loge(_(f"Failed to write configuration to file , error : {e}"))
        log.log(success.SaveConfigrationSuccess.value)
        return log.return_success(success.SaveConfigrationSuccess.value,{})

    # #########################################################################
    # Camera functions
    # #########################################################################

    def start_exposure(self, params: dict) -> dict:
        """
            Start the exposure of the camera | 开始曝光 \n
            Args : 
                params : {
                    "exposure" : float # exposure time
                    "gain" : int # gain
                    "offset" : int # offset
                    "binning" : int # binning
                    "roi" : {
                        "x" : int # x of the start position
                        "y" : int # y of the start position
                        "width" : int # width of the frame
                        "height" : int # height of the frame
                    }
                    "image" : {
                        "is_save" : bool
                        "is_dark" : bool
                        "name" : str
                        "type" : str # fits or tiff of jpg
                    }
                    "filterwheel" : {
                        "enable" : boolean # enable or disable
                        "filter" : int # id of filter
                    }
                }
            Returns : {
                "status" : int # status of the exposure
                "message" : str # message of the exposure
                "params" : None
            }
            NOTE : This function is a non-blocking function , 
                    you should call get_exposure_status to get the status of the exposure,
                    and after the exposure is complete successfully,
                    just call get_exposure_result to get the image
        """

    def abort_exposure(self) -> dict:
        """
            Abort exposure operation | 停止曝光
            Args: None
            Returns:{
                "status" : int,
                "message" : str
                "params" : None
            }
            NOTE : This function must be called if exposure is still in progress when shutdown server
        """

    def get_exposure_status(self) -> dict:
        """
            Get exposure status | 获取曝光状态
            Args: None
            Returns:{
                "status" : int,
                "message" : str
                "params" : {
                    "status" : int
                }
            }
        """

    def get_exposure_result(self) -> dict:
        """
            Get exposure result when exposure successful | 曝光成功后获取图像
            Args: None
            Returns:{
                "status" : int,
                "message" : str
                "params" : {
                    "image" : Base64 encoded image
                    "histogram" : List
                    "info" : Image Info
                }
            }
            NOTE : Format!
        """