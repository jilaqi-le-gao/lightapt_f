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

# System Library
import datetime
from json import JSONDecodeError, dumps
from secrets import randbelow
# Third Party Library

# Built-in Library
from server.basic.camera import BasicCameraAPI,BasicCameraInfo

import server.config as c

from utils.i18n import _
from utils.utility import switch
from utils.lightlog import lightlog
logger = lightlog(__name__)

class WsCameraInterface():
    """
        Websocket camera interface
    """

    def __init__(self) -> None:
        """
            Initialize the camera object
            Args : None
            Returns : None
        """
        self.info = BasicCameraInfo()
        self.device = None

    def __del__(self) -> None:
        """
            Cleanup the camera object
            Args : None
            Returns : None
        """
        if self.info._is_connected:
            self.device.disconnect()
        self.device = None

    def on_send(self, message : dict) -> bool:
        """
            Send message to client | 将信息发送至客户端
            Args:
                message: dict
            Returns: True if message was sent successfully
            Message Example:
                {
                    "status" : int ,
                    "message" : str,
                    "params" : dict
                }
        """
        if not isinstance(message, dict) or message.get("status") is None or message.get("message") is None:
            logger.loge(_("Unknown format of message"))
            return False
        try:
            c.ws.send_message_to_all(dumps(message))
        except JSONDecodeError as exception:
            logger.loge(_(f"Failed to parse message into JSON format , error {exception}"))
            return False
        return True 

    def remote_connect(self,params : dict) -> None:
        """
            Connect to the camera
            Args : 
                params : dict
                    "host" : str # default is "localhost"
                    "port" : int # port of the INDI or ASCOM server
                    "type" : str # default is "indi"
                    "name" : str # name of the camera , default is "CCD Simulator"
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the connection
                id : int # just a random number
                message : str # message of the connection
                params : info : BasicCameraInfo object
        """
        _host = params.get("host", "localhost")
        _port = int(params.get("port", 7624))
        _type = params.get("type", "indi")
        _name = params.get("name", "CCD Simulator")

        r = {
            "event" : "RemoteConnect",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        param = {
            "host" : _host,
            "port" : _port
        }
        # If the camera had already connected
        if self.info._is_connected:
            logger.logw(_("Camera is connected"))
            r["status"] = 2
            r["message"] = "Camera is connected"
            r["params"]["info"] = self.info.get_dict()
            return
        # Check if the type of the camera is supported
        if _type in ["indi","ascom"]:
            # Connect to ASCOM camera , the difference between INDI is the devie_number
            if _type == "ascom":    
                from server.driver.camera.ascom import AscomCameraAPI as ascom_camera
                self.device = ascom_camera()
                param["device_number"] = 0
            # Connect to INDI camera , the name of the device is needed
            elif _type == "indi":
                from server.driver.camera.indi import INDICameraAPI as indi_camera
                self.device = indi_camera()
                param["name"] = _name
            # Trying to connect the camera
            res = self.device.connect(params=param)
            if res.get('status') != 0:
                logger.loge(_(f"Failed to connect to {_host}:{_port}, error {res.get('status')}"))
                r["message"] = _("Failed to connect to camera")
                # If there is no error infomation
                try:
                    r["params"]["error"] = res.get('params').get('error')
                except:
                    pass
            else:
                r["status"] = 0
                r["message"] = _("Connected to camera successfully")
                r["params"]["info"] = res.get("params").get("info")
                self.info._is_connected = True
        # Unkown type of the camera
        else:
            logger.loge(_(f"Unknown type {_type}"))
            r["message"] = _("Unknown type")
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing connect command"))

    def remote_disconnect(self):
        """
            Disconnect from the camera
            Args : None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the disconnection
                id : int # just a random number
                message : str # message of the disconnection
                params : None
        """
        r = {
            "event" : "RemoteDisconnect",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }

        if not self.info._is_connected:
            logger.loge(_("Camera is not connected"))
            r["message"] = _("Camera is not connected")

        res = self.device.disconnect()
        if res.get('status')!= 0:
            logger.loge(_(f"Failed to disconnect from the camera"))
            r["message"] = _("Failed to disconnect from camera")
            try:
                r["params"]["error"] = res.get('params').get('error')
            except:
                pass
        else:
            r["status"] = 0
            r["message"] = _("Disconnected from camera successfully")
            self.info._is_connected = False
            logger.log(_("Disconnected from camera successfully"))
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing disconnect command"))

    def remote_reconnect(self) -> None:
        """
            Reconnect to the camera
            Args : None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the reconnection
                id : int # just a random number
                message : str # message of the reconnection
                params : info : BasicCameraInfo object
        """
        r = {
            "event" : "RemoteReconnect",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        res = self.device.reconnect()
        if res.get('status')!= 0:
            logger.loge(_(f"Failed to reconnect to the camera"))
            r["message"] = _("Failed to reconnect to camera")
            try:
                r["params"]["error"] = res.get('params').get('error')
            except:
                pass
        else:
            r["status"] = 0
            r["message"] = _("Reconnected to camera successfully")
            r["params"]["info"] = res.get("params").get("info")
            self.info._is_connected = True
            logger.log(_("Reconnected to camera successfully"))
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing reconnect command"))

    def remote_scanning(self) -> None:
        """
            Scannings from the camera
            Args : None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the scanning
                id : int # just a random number
                message : str # message of the scanning
                params : list : a list of camera name
        """
        r = {
            "event" : "RemoteScanning",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        res = self.device.scanning()
        if res.get('status')!= 0:
            logger.loge(_(f"Failed to scan from the camera"))
            r["message"] = _("Failed to scan camera")
            try:
                r["params"]["error"] = res.get('params').get('error')
                logger.log(_("Error : {}").format(r["params"]["error"]))
            except:
                pass
        else:
            r["status"] = 0
            r["message"] = _("Scannings from camera successfully")
            r["params"]["list"] = res.get("params").get("list")
            logger.log(_("Scanning camera successfully, found {} camera").format(len(r["params"]["list"])))

    def remote_polling(self) -> None:
        """
            Polling newest message from the camera
            Args : None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the polling
                id : int # just a random number
                message : str # message of the polling
                params : info : BasicCameraInfo object
        """
        r = {
            "event" : "RemotePolling",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        res = self.device.polling()
        if res.get('status')!= 0:
            logger.loge(_(f"Failed to poll from the camera"))
            r["message"] = _("Failed to poll camera")
            try:
                r["params"]["error"] = res.get('params').get('error')
                logger.loge(_("Error : {}").format(r["params"]["error"]))
            except:
                pass
        else:
            r["status"] = 0
            r["message"] = _("Polling camera successfully")
            r["params"]["info"] = res.get("params").get("info")
            logger.logd(_("Get camera information : {}").format(r["params"]["info"]))
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing polling command"))
    
    # #################################################################
    #
    # Camera control functions
    #
    # #################################################################

    def remote_start_exposure(self , params : dict) -> None:
        """
            Start the exposure of the camera
            Args :
                "params" : {
                    "exposure" : float # exposure time
                    "gain" : int # gain
                    "offset" : int # offset
                    "binning" : int # binning
                    "roi" : {
                        "height" : int # height of the camera frame
                        "width" : int # width of the camera frame
                        "start_x" : int # start x position of the camera frame
                        "start_y" : int # start y position of the camera frame
                    }
                    "image" : {
                        "is_save" : bool
                        "is_dark" : bool
                        "name" : str
                        "type" : str # fits or tiff of jpg
                    }
                }
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the exposure
                id : int # just a random number
                message : str # message of the exposure
                params : dict
            NOTE : This is a non-blocking function , will not return the result of the exposure
        """
        r = {
            "event" : "RemoteExposure",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        # If the exposure had already started
        if self.info._is_exposure:
            logger.loge(_(f"Exposure is already in progress"))
            r["message"] = _("Exposure is already in progress")
            if self.on_send(r) is False:
                logger.loge(_(f"Failed to send message while executing exposure command"))
            return

        _exposure = params.get("exposure")
        _gain = params.get("gain")
        _offset = params.get("offset")
        _binning = params.get("binning")
        _roi = params.get("roi")
        _image = params.get("image")

        flag = False
        # Check if the value of exposure is valid
        if _exposure is None or not isinstance(_exposure,float) or not 0 < _exposure < 3600:
            logger.loge(_(f"Invalid exposure time : {_exposure}"))
            r["message"] = _("Invalid exposure time")
            r["params"]["error"] = _exposure
            flag = True
        # Check if the gain is changed and whether the value is correct
        if _gain is not None and (not isinstance(_gain,int) or not 0 < _gain < 100):
            logger.loge(_(f"Invalid gain : {_gain}"))
            r["message"] = _("Invalid gain")
            r["params"]["error"] = _gain
            flag = True
        # Check if the offset is changed and whether the value is correct
        if _offset is not None and (not isinstance(_offset,int) or not 0 < _offset < 100):
            logger.loge(_(f"Invalid offset : {_offset}"))
            r["message"] = _("Invalid offset")
            r["params"]["error"] = _offset
            flag = True
        # Check if the binning is changed and whether the value is correct
        if _binning is not None and (not isinstance(_binning,int) or not 0 < _binning <= 8):
            logger.loge(_(f"Invalid binning : {_binning}"))
            r["message"] = _("Invalid binning")
            r["params"]["error"] = _binning
            flag = True
        # If any of the parameters is invalid
        if flag:
            if self.on_send(r) is False:
                logger.loge(_(f"Failed to send message while executing exposure command"))
            return

        # If the ROI setting is None , just use the biggest frame
        if _roi is None:
            _roi = {
                "height" : self.info._height,
                "width" : self.info._width,
                "start_x" : 0,
                "start_y" : 0
            }
        else:
            # Check if the height and width of image are provided and if they are correct. If not , use the biggest frame
            _roi["height"] = _roi.get("height") if _roi.get("height") is not None and 0 < _roi.get("height") < self.info._max_height else self.info._max_height
            _roi["width"] = _roi.get("width") if _roi.get("width") is not None and 0 < _roi.get("width") < self.info._max_width else self.info._max_width
            # Check if the start_x and start_y are provided and if they are correct
            _roi["start_x"] = _roi.get("start_x") if _roi.get("start_x") is not None and 0 < _roi.get("start_x") < self.info._max_width else 0
            _roi["start_y"] = _roi.get("start_y") if _roi.get("start_y") is not None and 0 < _roi.get("start_y") < self.info._max_height else 0
        # If the Image setting is empty
        if _image is None:
            _image = {
                "is_save": True,
                "is_dark" : False,
                "name" : datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "type" : "fits"
            }
        # Generate the parameters
        param = {
            "exposure" : _exposure,
            "gain" : _gain,
            "offset" : _offset,
            "binning" : _binning,
            "roi" : _roi,
            "image" : _image
        }
        # Start exposure
        res = self.device.start_exposure(params=param)
        if res.get("status") != 0:
            r["message"] = res.get("message")
            try:
                r["params"]["error"] = res.get("params").get("error")
            except:
                pass
        else:
            r["message"] = _("Exposure started")
            self.info._is_exposure = True
        if self.on_send(r) is False:
            logger.loge(_(f"Failed to send message while executing exposure command"))

    def remote_abort_exposure(self) -> None:
        """
            Abort exposure | 停止曝光
            Args : None
            Returns : None
            ClientReturn:
                event : str # name of the event
                id : int # just a random number
                status : int # status of the event
                message : str # message of the event
                params : dict # default is None
            NOTE : This function must be called if the server is shutting down while exposure
        """
        r = {
            "event" : "RemoteAbortExposure",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        # Check if the exposure is not started
        if not self.info._is_exposure:
            logger.loge(_("Exposure is not started"))
            r["message"] = _("Exposure is not started")
            if self.on_send(r) is False:
                logger.loge(_(f"Failed to send message while executing aborting exposure command"))
            return
        # Trying to stop the exposure
        res = self.device.stop_exposure()
        if res.get("status")!= 0:
            r["message"] = res.get("message")
            try:
                r["params"]["error"] = res.get("params").get("error")
            except:
                pass
        else:
            r["message"] = res.get("message")
            self.info._is_exposure = False
        if self.on_send(r) is False:
            logger.loge(_(f"Failed to send message while executing aborting exposure command"))

    def remote_get_exposure_status(self) -> None:
        """
            Get exposure status | 停止曝光
            Args : None
            Returns : None
            ClientReturn:
                event : str # name of the event
                id : int # just a random number
                status : int # status of the event
                message : str # message of the event
                params : dict # default is None
            NOTE : This function should be called during the exposure process
        """
        r = {
            "event" : "RemoteGetExposureStatus",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        # Check if the exposure is not started
        if not self.info._is_exposure:
            logger.loge(_("Exposure is not started"))
            r["message"] = _("Exposure is not started")
            if self.on_send(r) is False:
                logger.loge(_(f"Failed to send message while executing get_exposure_status command"))
            return
        # Trying to get the status of exposure
        res = self.device.get_exposure_status()
        if res.get("status")!= 0:
            r["message"] = res.get("message")
            try:
                r["params"]["error"] = res.get("params").get("error")
            except:
                pass
        else:
            r["message"] = res.get("message")
            # Why python doesn't support continuous assignment
            r["params"]["status"] = res.get("params").get("status")
            self.info._is_exposure = res.get("params").get("status")
        if self.on_send(r) is False:
            logger.loge(_(f"Failed to send message while executing get_exposure_status command"))

    def remote_get_exposure_result(self) -> None:
        """
            Get exposure result | 获取曝光结果
            Args : None
            Returns : None
            ClientReturn:
                event : str # name of the event
                id : int # just a random number
                status : int # status of the event
                message : str # message of the event
                params : dict # default is None
            NOTE : This function should be called after the exposure is finished successfully
        """
        r = {
            "event" : "RemoteGetExposureResult",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        # Check if the exposure is not finished
        if self.info._is_exposure:
            r["message"] = _("Exposure is not finished")
            if self.on_send(r) is False:
                logger.loge(_(f"Failed to send message while executing get_exposure_result command"))
            return
        # Trying to get the result of exposure
        res = self.device.get_exposure_result()
        if res.get("status")!= 0:
            r["message"] = res.get("message")
            try:
                r["params"]["error"] = res.get("params").get("error")
            except:
                pass
        else:
            r["message"] = res.get("message")
            # Get the base64 encoded image data
            r["params"]["image"] = res.get("params").get("image")
            # Get the histogram of the image
            r["params"]["histogram"] = res.get("params").get("histogram")
            # Get the infomation of the image
            r["params"]["info"] = res.get("params").get("info")
        if self.on_send(r) is False:
            logger.loge(_(f"Failed to send message while executing get_exposure_result command"))

    def remote_start_sequence_exposure(self,params : dict) -> None:
        """
            Start exposure sequence
            Args : 
                params : dict
                    "number" : int # number of sequences
                    "sequence" : list
                        start_time : time string , format is "YYYY-MM-DD-hh:mm:ss"
            Returns : None
            ClientReturn:
                event : str # name of the event
                id : int # just a random number
                status : int # status of the event
                message : str # message of the event
                params : dict # default is None
            NOTE : This function's parameters should be thinked carefully
        """
