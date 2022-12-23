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

from server.basic.guider import TcpSocket,BasicGuiderAPI,BasicGuiderInfo
from utils.utility import switch
from utils.lightlog import lightlog
log = lightlog(__name__)

import gettext
_ = gettext.gettext

import json
import socket
import threading

class SettleParams():
    """
        The SETTLE parameter is used by the guide and dither commands to specify when PHD2 should consider guiding to be stable enough for imaging. \n
        SETTLE is an object with the following attributes:
    """
    pixels = 1.5 # maximum guide distance for guiding to be considered stable or "in-range"
    time : 8 # minimum time to be in-range before considering guiding to be stable
    timeout : 40 # time limit before settling is considered to have failed

    def get_dict(self) -> dict:
        return {
            "pixels": self.pixels,
            "time": self.time,
            "timeout": self.timeout
        }

class CalibrationModel(object):
    """
        Calibration models for calibration
    """
    xAngle : float
    xRate : float
    xParity : float
    yAngle : float
    yRate : float
    yParity : float
    
    def get_dict(self) -> dict:
        return {
            'xAngle': self.xAngle,
            'xRate': self.xRate,
            'xParity': self.xParity,
            'yAngle': self.yAngle,
            'yRate': self.yRate,
            'yParity': self.yParity,
        }

class CoolingModel(object):
    """
        Cooling models for cooling
    """
    _temperature : float
    _is_cooling : bool
    _target_temperature : float
    _cooling_power : float

    def get_dict(self) -> dict:
        return {
            "temperature": self._temperature,
            "is_cooling": self._is_cooling,
            "target_temperature": self._target_temperature,
            "cooling_power": self._cooling_power,
        }

class EquipmentModel(object):
    """
        Equipment models for equipment
    """
    _camera_name : str
    _is_camera_connected = False

    _mount_name : str
    _is_mount_connected = False

    _aux_mount_name : str
    _is_aux_mount_connected = False

    _ao_name : str
    _is_ao_connected = False

    def get_dict(self) -> dict:
        return {
            "camera" : {
                "name" : self._camera_name,
                "is_connected" : self._is_camera_connected,
            },
            "mount" : {
                "name" : self._mount_name,
                "is_connected" : self._is_mount_connected,
            },
            "aux_mount" : {
                "name" : self._aux_mount_name,
                "is_connected" : self._is_aux_mount_connected,
            },
            "ao" : {
                "name" : self._ao_name,
                "is_connected" : self._is_ao_connected,
            }
        }

class CalibrationStatus(object):
    """
        Calibration status container
    """
    _model = CalibrationModel()
    _direction : str   # calibration direction (phase)
    _distance : float  # distance from starting location
    _dx : float    # x offset from starting position
    _dy : float    # y offset from starting position
    _position = [] # star coordinates
    _step : int # step number
    _state : str   # calibration status message
    _flip : bool # flip calibration data

    def get_dict(self) -> dict:
        return {
            "model": self._model.get_dict(),
            "direction": self._direction,
            "distance": self._distance,
            "dx": self._dx,
            "dy": self._dy,
            "position": self._position,
            "step": self._step,
            "state": self._state,
            "flip": self._flip
        }

class GuidingStatus(object):
    """
        Guiding status container
    """
    _frame : int # The frame number; starts at 1 each time guiding starts
    _time : int # the time in seconds, including fractional seconds, since guiding started
    _last_error : int # error code
    _output_enabled : bool # whether output is enabled

    _dx : float # the X-offset in pixels
    _dy : float # the Y-offset in pixels

    _average_distance : float # a smoothed average of the guide distance in pixels

    _ra_raw_distance : float # the RA distance in pixels of the guide offset vector
    _dec_raw_distance : float # the DEC distance in pixels of the guide offset vector
    _ra_distance : float # the guide algorithm-modified RA distance in pixels of the guide offset vector
    _dec_distance : float # the guide algorithm-modified DEC distance in pixels of the guide offset vector
    
    _ra_duration : float # the RA guide pulse duration in milliseconds
    _dec_distance : float # the DEC guide pulse duration in milliseconds

    _ra_direction : str # "East" or "West"
    _dec_direction : str # "North" or "South"

    _ra_limited : bool # true if step was limited by the Max RA setting (attribute omitted if step was not limited)
    _dec_limited : bool # true if step was limited by the Max DEC setting (attribute omitted if step was not limited)
    
    _pixel_scale : float
    _search_region : float
    _starmass : float # the Star Mass value of the guide star
    _snr : float # the computed Signal-to-noise ratio of the guide star
    _hfd : float # the guide star half-flux diameter (HFD) in pixels
    
    def get_dict(self) -> dict:
        return {
            "frame" : self._frame,
            "time" : self._time,
            "last_error" : self._last_error,
            "output_enabled" : self._output_enabled,
            "dx" : self._dx,
            "dy" : self._dy,
            "average_distance" : self._average_distance,
            "ra" : {
                "raw_distance" : self._ra_raw_distance,
                "distance" : self._ra_distance,
                "duration" : self._ra_duration,
                "direction" : self._ra_direction,
                "limited" : self._ra_limited,
            },
            "dec" : {
                "raw_distance" : self._dec_raw_distance,
                "distance" : self._dec_distance,
                "duration" : self._dec_duration,
                "direction" : self._dec_direction,
                "limited" : self._dec_limited,
            },
            "image" : {
                "starmass" : self._starmass,
                "snr" : self._snr,
                "hfd" : self._hfd,
                "pixel_scale" : self._pixel_scale,
            }
        }

class ImageInfo(object):
    """
        Image information container
    """
    _frame : int
    _height : int
    _width : int
    _star_pos : list
    _image : str

    def get_dict(self) -> dict:
        return {
            "frame" : self._frame,
            "height" : self._height,
            "width" : self._width,
            "star_pos" : self._star_pos,
            "image" : self._image,
        }

class PHD2ClientInfo(BasicGuiderInfo):
    """
        PHD2 client information container
    """

    version : str
    subversion : str
    msgversion : str
    state : str
    profile : dict

    mount : str
    frame : int
    exposure = 500 # milliseconds
    subframe = [] # subframe of exposure

    cooling_model = CoolingModel()

    equipment_model = EquipmentModel()

    g_status = GuidingStatus()

    c_status = CalibrationStatus()

    image = ImageInfo()

    _settle_distance : float
    _settle_time : float
    _settle_star_locked : bool
    _settle_total_frame : int
    _settle_drop_frame : int

    _lock_position_x : int
    _lock_position_y : int
    _lock_shift_enabled : bool
    
    star_selected_x : int   # lock position X-coordinate
    star_selected_y : int # lock position Y-coordinate

    dither_dx : float # the dither X-offset in pixels
    dither_dy : float # the dither Y-offset in pixels

    starlost_snr : float
    starlost_starmass : float
    starlost_avgdist : float

class PHD2Client(BasicGuiderAPI):
    """
        PHD2 client based on TCP/IP connection
    """

    def __init__(self) -> None:
        self.conn = TcpSocket()
        self.terminate = False
        self._background_task = None
        self.info = PHD2ClientInfo()
        self.response = None
        self.lock = threading.Lock()
        self.cond = threading.Condition()

    def __del__(self) -> None:
        if self.info._is_guiding:
            self.abort_guiding()
        if self.info._is_calibrating:
            self.abort_calibrating()
        if self.info._is_connected:
            self.disconnect()

    # #################################################################
    #
    # Public from parent class
    #
    # #################################################################

    def connect(self, params: dict) -> dict:
        """
            Connect to PHD2 | 连接PHD2
            Args: 
                params:{
                    "host": str,    # default host is "127.0.0.1"
                    "port": int     # default port is 4400
                }
            Returns:{
                "status" : int,
                "message": str,
                "params" : None
            }
        """
        host = params.get("host", "127.0.0.1")
        port = int(params.get("port", 4400))
        log.log(_(f"Try to connect to PHD2 server on {host}:{port}"))
        try:
            self.conn.connect(host, port)
            self.terminate = False
            self.info._is_connected = True
            self._background_task = threading.Thread(target=self.background_task)
            self._background_task.start()
        except OSError as e:
            log.loge(_("Failed to connect to PHD2 server"))
            return log.return_error(_("Failed to connect to PHD2 server"),{"error" :e})
        log.log(_("Connected to PHD2 server successfully"))
        return log.return_success(_("Connected to PHD2 server successfully"),{})

    def disconnect(self) -> dict:
        """
            Disconnect from PHD2 | 连接PHD2
            Args : None
            Returns:{
                "status" : int,
                "message": str,
                "params" : None
            }
            NOTE : This function must be called before shutting down the server
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 is not connected , please do not execute disconnect() command"))
            return log.return_error(_("PHD2 is not connected"),{})
        self.conn.disconnect()
        self.info._is_connected = False
        self.terminate = True
        log.log(_("Disconnect from PHD2 successfully"))
        return log.return_success(_("Disconnect from PHD2 successfully"),{})

    def reconnect(self) -> dict:
        """
            Reconnect to PHD2 | 重新连接PHD2
            Args: 
                None
            Returns:{
                "status" : int,
                "message": str,
                "params" : None
            }
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 is not connected, please do not execute reconnect() command"))
            return log.return_error(_("PHD2 is not connected"),{})
        self.conn.disconnect()
        log.logd(_("Disconnect from PHD2 ..."))
        self.conn.connect()
        self.info._is_connected = True
        self._background_task = threading.Thread(target=self.background_task)
        self._background_task.start()
        log.log(_("Reconnecting to PHD2 successfully"))
        return log.return_success(_("Reconnecting to PHD2 successfully"),{})

    def scanning(self) -> dict:
        """
            Scan PHD2 server | 扫描PHD2服务器
            Args: 
                None
            Returns:{
                "status" : int,
                "message": str,
                "params" : {
                    "guider" : list
                }
            }
        """
        log.log(_("Start scanning PHD2 server ..."))
        guider_list = []
        for port in range(4400,4406):
            try:
                connSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                connSkt.connect(("127.0.0.1",port))
                log.log(_(f"Found socket port open on {port}"))
                guider_list.append(port)
            except:
                log.logd(_(f"Scanning socket port {port} failed"))
        if len(guider_list) == 0:
            log.logd(_(f"No PHD2 server found"))
            return log.return_error(_(f"No PHD2 server found"),{})
        log.log(_(f"Found PHD2 server open on {guider_list}"))
        return log.return_success(_(f"Found PHD2 server"),{"guider" : guider_list})

    # #################################################################
    #
    # Listen and progress messages from PHD2 server
    #
    # #################################################################

    def background_task(self) -> None:
        """
            Background task listen server message | 获取PHD2信息
            Args:
                None
            Returns:
                None
        """
        while not self.terminate:
            line = self.conn.read()
            if not line:
                if not self.terminate:
                    pass
                break
            try:
                j = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "jsonrpc" in j:
                with self.cond:
                    self.response = j
                    self.cond.notify()
            else:
                self.parser_json(j)

    def parser_json(self, params : dict) -> None:
        """
            Parser JSON message | JSON信息解析器
            Args:
                params:{
                    "message": dict,
                }
            Returns:
                None
        """
        if params is None:
            return
        log.log(f"{params}")

        event = params.get('Event')
        message = params

        for case in switch(event):
            if case("Version"):
                self._version(message)
                break
            if case("LockPositionSet"):
                self._lock_position_set(message)
                break
            if case("Calibrating"):
                self._calibrating(message)
                break
            if case("CalibrationComplete"):
                self._calibration_completed(message)
                break
            if case("StarSelected"):
                self._star_selected(message)
                break
            if case("StartGuiding"):
                self._start_guiding()
                break
            if case("Paused"):
                self._paused()
                break
            if case("StartCalibration"):
                self._start_calibration(message)
                break
            if case("AppState"):
                self._app_state(message)
                break
            if case("CalibrationFailed"):
                self._calibration_failed(message)
                break
            if case("CalibrationDataFlipped"):
                self._calibration_data_flipped(message)
                break
            if case("LockPositionShiftLimitReached"):
                self._lock_position_shift_limit_reached()
                break
            if case("LoopingExposures"):
                self._looping_exposures(message)
                break
            if case("LoopingExposuresStopped"):
                self._looping_exposures_stopped()
                break
            if case("SettleBegin"):
                self._settle_begin()
                break
            if case("Settling"):
                self.settling(message)
                break
            if case("SettleDone"):
                self._settle_done(message)
                break
            if case("StarLost"):
                self._star_lost(message)
                break
            if case("GuidingStopped"):
                self._guiding_stopped()
                break
            if case("Resumed"):
                self._resumed()
                break
            if case("GuideStep"):
                self._guide_step(message)
                break
            if case("GuidingDithered"):
                self._guiding_dithered(message)
                break
            if case("LockPositionLost"):
                self._lock_position_lost()
                break
            if case("Alert"):
                self._alert(message)
                break
            if case("GuideParamChange"):
                self._guide_param_change(message)
                break
            if case("ConfigurationChange"):
                self._configuration_change()
                break
            log.loge(_(f"Unknown event : {event}"))
            break

    def _version(self,message : dict) -> None:
        """
            Get PHD2 version
            Args:
                None
            Returns:
                None
        """
        self.info.version = message.get("PHDVersion")
        log.logd(_(f"PHD2 version : {self.info.version}"))
        self.info.subversion = message.get("PHDSubver")
        log.logd(_(f"PHD2 subversion : {self.info.subversion}"))
        self.info.msgversion = message.get("MsgVersion")
        log.logd(_(f"PHD2 message version : {self.info.msgversion}"))

    def _lock_position_set(self, message : dict) -> None:
        """
            Get lock position set
            Args:
                message : dict
            Returns:
                None
        """
        self.info._lock_position_x = message.get("X")
        self.info._lock_position_y = message.get("Y")
        log.logd(_(f"Star lock position : {[self.info._lock_position_x, self.info._lock_position_y]}"))

    def _calibrating(self,message : dict) -> None:
        """
            Get calibrating state
            Args:
                message : dict
            Returns:
                None
        """
        self.info.c_status._direction = message.get("dir")
        log.logd(_(f"Star calibrating direction : {self.info._is_calibrating}"))
        self.info.c_status._distance = message.get("dist")
        log.logd(_(f"Star calibrating distance : {self.info.c_status._distance}"))
        self.info.c_status._dx = message.get("dx")
        log.logd(_(f"Star calibrating dx : {self.info.c_status._dx}"))
        self.info.c_status._dy = message.get("dy")
        log.logd(_(f"Star calibrating dy : {self.info.c_status._dy}"))
        self.info.c_status._position = message.get("pos")
        log.logd(_(f"Star calibrating position : {self.info.c_status._position}"))
        self.info.c_status._step = message.get("step")
        log.logd(_(f"Star calibrating step : {self.info.c_status._step}"))
        self.info.c_status._state = message.get("State")
        log.logd(_(f"Star calibrating state : {self.info.c_status._state}"))

    def _calibration_completed(self,message : dict) -> None:
        """
            Get calibration completed state
            Args:
                message : dict
            Returns:
                None
        """
        self.info.mount = message.get("Mount")
        log.logd(_(f"Mount : {self.info.mount}"))

    def _star_selected(self,message : dict) -> None:
        """
            Get star selected state
            Args:
                message : dict
            Returns:
                None
        """
        self.info.star_selected_x = message.get("X")
        self.info.star_selected_y = message.get("Y")
        log.logd(_(f"Star selected position : [{self.info.star_selected_x},{self.info.star_selected_y}]"))
    
    def _start_guiding(self) -> None:
        """
            Get start guiding state
            Args:
                message : dict
            Returns:
                None
        """
        self.info._is_guiding = True
        log.logd(_(f"Start guiding"))

    def _paused(self) -> None:
        """
            Get paused state
            Args:
                None
            Returns:
                None
        """
        self.info._is_guiding = False
        log.log(_("Guiding is paused"))

    def _start_calibration(self, message : dict) -> None:
        """
            Get start calibration state
            Args:
                message : dict
            Returns:
                None
        """
        self.info.mount = message.get("Mount")
        self.info._is_calibrating = True
        log.log(_("Start calibration"))

    def _app_state(self, message : dict) -> None:
        """
            Get app state
            Args:
                message : dict
            Returns:
                None
        """
        self.info.state = message.get("State")
        log.logd(_(f"App state : {self.info.state}"))

    def _calibration_failed(self, message : dict) -> None:
        """
            Get calibration failed state
            Args:
                message : dict
            Returns:
                None
        """
        self.info.last_error = message.get("Reason")
        self.info._is_calibrating = False
        self.info._is_calibrated = False
        log.loge(_(f"Calibration failed , error : {self.info.last_error}"))

    def _calibration_data_flipped(self, message : dict) -> None:
        """
            Get calibration data flipping state
            Args:
                message : dict
            Returns:
                None
        """
        self.info.c_status._flip = True
        log.log(_("Calibration data flipped"))

    def _lock_position_shift_limit_reached(self) -> None:
        """
            Get lock position shift limit reached state
            Args:
                None
            Returns:
                None
        """
        log.logw(_("Star locked position reached the edge of the camera frame"))

    def _looping_exposures(self, message : dict) -> None:
        """
            Get looping exposures state
            Args:
                message : dict
            Returns:
                None
        """
        self.info._is_looping = True
        self.info.frame = message.get("Frame")

    def _looping_exposures_stopped(self) -> None:
        """
            Get looping exposures stopped state
            Args:
                None
            Returns:
                None
        """
        self.info._is_looping = False

    def _settle_begin(self) -> None:
        """
            Get settle begin state
            Args:
                None
            Returns:
                None
        """
        self.info._is_settling = True
        log.log(_("Star settle begin ..."))

    def _settling(self , message : dict) -> None:
        """
            Get settling state
            Args:
                message : dict
            Returns:
                None
        """
        self.info._settle_distance = message.get("Distance")
        self.info._settle_time = message.get("SettleTime")
        self.info._settle_star_locked = message.get("StarLocked")
        self.info._is_settling = True

    def _settle_done(self, message : dict) -> None:
        """
            Get settle done state
            Args:
                message : dict
            Returns:
                None
        """
        status = message.get("Status")
        if status == 0:
            log.log(_("Settle succeeded"))
            self.info._is_settled = True
        else:
            log.log(_(f"Settle failed , error : {message.get('Error')}"))
            self.info._is_settled = False
        self.info._is_settling = False

    def _star_lost(self, message : dict) -> None:
        """
            Get star lost state
            Args:
                message : dict
            Returns:
                None
        """
        self.info.frame = message.get('Frame')
        self.info.starlost_snr = message.get('SNR')
        self.info.starlost_starmass = message.get('StarMass')
        self.info.starlost_avgdist = message.get('AvgDist')
        log.loge(_(f"Star Lost , Frame : {self.info.frame} , SNR : {self.info.starlost_snr} , StarMass : {self.info.starlost_starmass} , AvgDist : {self.info.starlost_avgdist}"))
        self.info._is_starlost = True

    def _guiding_stopped(self) -> None:
        """
            Get guiding stopped state
            Args:
                None
            Returns:
                None
        """
        self.info._is_guiding = False
        log.log(_("Guiding Stopped"))

    def _resumed(self) -> None:
        """
            Get guiding resumed state
            Args:
                None
            Returns:
                None
        """
        log.log(_("Guiding Resumed"))
        self.info._is_guiding = True

    def _guide_step(self , message : dict) -> None:
        """
            Get guide step state
            Args:
                message : dict
            Returns:
                None
        """
        self.info.g_status._frame = message.get("Frame")
        self.info.mount = message.get("Mount")
        self.info.g_status._error = message.get("ErrorCode")

        self.info.g_status._average_distance = message.get("AvgDist")

        self.info.g_status._dx = message.get("dx")
        self.info.g_status._dy = message.get("dy")

        self.info.g_status._ra_raw_distance = message.get("RADistanceRaw")
        self.info.g_status._dec_raw_distance = message.get("DECDistanceRaw")

        self.info.g_status._ra_distance = message.get("RADistanceGuide")
        self.info.g_status._dec_distance = message.get("DECDistanceGuide")

        self.info.g_status._ra_duration = message.get("RADuration")
        self.info.g_status._dec_duration = message.get("DECDuration")

        self.info.g_status._ra_direction = message.get("RADirection")
        self.info.g_status._dec_direction = message.get("DECDirection")    

        self.info.g_status._snr = message.get("SNR")
        self.info.g_status._starmass = message.get("StarMass")
        self.info.g_status._hfd = message.get("HFD")
        
    def _guiding_dithered(self, message : dict) -> None:
        """
            Get guiding dithered state
            Args:
                message : dict
            Returns:
                None
        """
        self.info.dither_dx = message.get("dx")
        self.info.dither_dy = message.get("dy")

    def _lock_position_lost(self) -> None:
        """
            Get lock position lost state
            Args:
                None
            Returns:
                None
        """
        self.info._is_starlocklost = True
        log.loge(_(f"Lock Position Lost"))

    def _alert(self, message : dict) -> None:
        """
            Get alert state
            Args:
                message : dict
            Returns:
                None
        """
        log.loge(_(f"Alert : {message.get('Msg')}"))

    def _guide_param_change(self, message : dict) -> None:
        """
            Get guide param change state
            Args:
                message : dict
            Returns:
                None
        """
    
    def _configuration_change(self) -> None:
        """
            Get configuration change state
            Args:
                None
            Returns:
                None
        """

    # #################################################################
    #
    # Send commands to the PHD2 server
    #
    # #################################################################

    def generate_command(self, command : str, params : dict) -> dict:
        """
            Generate command to send to the PHD2 server
            Args:
                command : str
                params : dict
            Returns:
                dict
        """
        res = {
            "method": command,
            "id" : 1
        }
        if params is not None:
            if isinstance(params, (list, dict)):
                res["params"] = params
            else:
                res["params"] = [ params ]
        return res

    def send_command(self, command : dict) -> dict:
        """
            Send command to the PHD2 server
            Args:
                command : dict
            Returns:
                bool
        """
        r = json.dumps(command,separators=(',', ':'))
        self.conn.send(r + "\r\n")
        # wait for response
        with self.cond:
            while not self.response:
                self.cond.wait()
            response = self.response
            self.response = None
        if "error" in response:
            log.loge(_(f"Guiding Error : {response.get('error').get('message')})"))
        return response

    def _capture_single_frame(self,params : dict) -> dict:
        """
            Capture a single frame | 单张拍摄
            Args:
                params : {
                    "exposure" : int # milliseconds
                    "subframe" : {
                        "height" : int
                        "width" : int
                        "x" : int
                        "y" : int
                    }
                }
            Returns:{
                "status" : int,
                "message" : str
                "params" : dict
            }
            NOTE : captures a singe frame; guiding and looping must be stopped first
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        # Check if server is guiding
        if self.info._is_guiding:
            log.loge(_("Is guiding now , please stop guiding before capturing a single frame"))
            return log.return_error(_("Guiding now"),{})
        # Check if server is looping
        if self.info._is_looping:
            log.loge(_("Is looping now, please stop looping before capturing a single frame"))
            return log.return_error(_("Looping now"),{})
        # Check if the parameters are valid
        exposure = params.get("exposure", self.info.exposure)
        subframe = params.get("subframe", self.info.subframe)
        if exposure is not None:
            if not isinstance(exposure,int) or exposure < 0:
                log.loge(_(f"Unreadable exposure value : {exposure}"))
                return log.return_error(_("Invalid exposure value"),{})
        if subframe is not None:
            pass
        _params = {
            "exposure" : exposure,
        }
        # However both exposure and subframe are optional
        command = self.generate_command("capture_single_frame",_params)
        try:
            res = self.send_command(command)
            log.logd(_(f"Captured single frame result : {res}"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server , error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{})
        log.log(_("Send capture single frame command to PHD2 server"))
        return log.return_success(_("Sent single frame command to PHD2 server"),{})

    def _clear_calibration(self, params : dict) -> dict:
        """
            Clear calibration data | 清楚校准数据
            Args:
                params : {
                    "type": str # "ao" or "mount" or "both",
                }
            Returns:
                dict
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        _type = params.get("type")
        if _type is None or _type not in ["mount", "both", "ao"]:
            log.loge(_("Please provide a type of what calibration data you want to clear"))
            return log.return_error(_("Invalid type"),{})
        command = self.generate_command("clear_calibration",_type)
        try:
            res = self.send_command(command)
            log.logd(_(f"Cleared calibration result : {res}"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server , error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{})
        log.log(_("Send clear calibration command to PHD2 server"))
        self.info._is_calibrated = False
        return log.return_success(_("Sent clear calibration command to PHD2 server"),{})

    def _dither(self, params : dict) -> dict:
        """
            Dither | 抖动\n
            Args:
                params : {
                    "amount" : float # amount in pixels
                    "raonly" : bool # default is false
                    "settle" : SettleParams object
                }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE :  The dither method allows the client to request a random shift of the lock position by +/- PIXELS on each of the RA and Dec axes. 
                    If the RA_ONLY parameter is true, or if the Dither RA Only option is set in the Brain, the dither will only be on the RA axis. 
                    The PIXELS parameter is multiplied by the Dither Scale value in the Brain.
                    Like the guide method, the dither method takes a SETTLE object parameter. 
                    PHD will send Settling and SettleDone events to indicate when guiding has stabilized after the dither.
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        amount = params.get('amount',1.5)
        raonly = params.get('raonly',False)
        settle = params.get('settle')
        if raonly:
            log.logd(_("Set Dither RA only"))
        if amount < 0:
            log.loge(_(f"Invalid amount value : {amount} , use default value : 10"))
            amount = 10
        if settle is None:
            settle = SettleParams()
            log.logd(_(f"Settle object not provided, using default value"))
        _params = {
            "amount" : amount,
            "raOnly" : raonly,
            "settle" : {
                "pixels" : settle.pixels,
                "time" : settle.time,
                "timeouts" : settle.timeout
            }
        }
        command = self.generate_command("dither",_params)
        try:
            res = self.send_command(command)
            log.logd(_("Sent dither command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"Dither command failed , error : {res.get('error')}"))
            return log.return_error(_("Dither command failed"),{"error":res.get('error')})
        log.log(_("Sent dither command to PHD2 server successfully"))
        return log.return_success(_("Sent dither command to PHD2 server"),{})
            

    def _find_star(self, params : dict) -> dict:
        """
            Auto select a star | 自动寻星
            Args:
                params : {
                    "roi" : [
                        "x" : int,
                        "y" : int,
                        "width" : int,
                        "height" : int
                    ]   # default is full frame
                }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : on success: returns the lock position of the selected star, otherwise returns an error object
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        roi = params.get('roi')
        _params = None
        if roi is not None:
            x = roi.get('x')
            y = roi.get('y')
            width = roi.get('width')
            height = roi.get('height')
            log.logd(_(f"Auto selection frame setting : x={x} , y={y} , width={width} , height={height}"))
            _params = {
                "roi" : [x,y,width,height]
            }
        command = self.generate_command("find_star",_params)
        try:
            res = self.send_command(command)
            log.log(_("Sent auto select a star command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error" : e})
        if "error" in res:
            log.loge(_(f"PHD2 auto find star error : {res.get('error')}"))
        else:
            result = res.get("result")
            self.info.star_selected_x = result[0]
            self.info.star_selected_y = result[1]
            log.log(_(f"Star selected at position : [{self.info.star_selected_x}, {self.info.star_selected_y}]"))
            self.info._is_selected = True
        return log.return_success(_("Star Selected"),{"position":res.get('result')})

    def _flip_calibration(self) -> dict:
        """
            Flip calibration data | 反转校准数据
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        if not self.info._is_calibrated:
            log.loge(_("Guider had not calibrated , please do not execute flip_calibration() command"))
            return log.return_error(_("Guider had not calibrated"),{})
        command = self.generate_command("flip_calibration")
        try:
            res = self.send_command(command)
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error": e})
        if "error" in res:
            log.loge(_(f"PHD2 flip_calibration error : {res.get('error')}"))
            return log.return_error(_("PHD2 flip_calibration error"),{"error":res.get('error')})
        log.log(_("Calibration data flipped successfully"))
        return log.return_success(_("Calibration data flipped successfully"),{})

    def _get_algo_param_names(self,params : dict) -> dict:
        """
            Get guide algorithm parameters | 获取导星算法参数
            Args:
                params : {
                    "type" : str # "x","y","ra","dec"
                }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        if "type" not in params:
            log.loge(_(f"Guide algorithm type is not set"))
            return log.return_error(_(f"Guide algorithm type is not set"),{})
        if params["type"] not in ["x","y","ra","dec"]:
            log.loge(_("Unknown guide algorithm type"))
            return log.return_error(_("Unknown guide algorithm"),{})
        _params = {
            "type" : params.get("type")
        }
        command = self.generate_command("get_algo_param_names",_params)
        try:
            res = self.send_command(command)
            log.logd(_("Sent get algorithms parameters command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error": e})
        if "error" in res:
            log.loge(_(f"PHD2 get_algo_param_names error : {res.get('error')}"))
            return log.return_error(_("PHD2 get_algo_param_names error"),{"error":res.get('error')})
        log.logd(_("PHD2 get_algo_param_names successfully"))
        return log.return_success(_("PHD2 get_algo_param_names successfully"),{"value":res.get('result')})
    
    def _get_algo_param(self,params : dict) -> dict:
        """
        
        """

    def _get_app_state(self) -> dict:
        """
            Get app state | 获取导星状态
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : 	same value that came in the last AppState notification
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        log.logd(_("Trying to get app state ... "))
        command = self.generate_command("get_app_state")
        try:
            res = self.send_command(command)
            log.logd(_("Sent get app state command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"PHD2 get_app_state error : {res.get('error')}"))
            return log.return_error(_("PHD2 get_app_state error"),{"error":res.get('error')})
        log.logd(_("PHD2 get_app_state successfully"))
        return log.return_success(_("PHD2 get_app_state successfully"),{"status":res.get('status')})

    def _get_camera_frame_size(self) -> dict:
        """
            Get camera frame size | 获取相机画幅大小
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        log.logd(_("Trying to get camera frame size... "))
        command = self.generate_command("get_camera_frame_size")
        try:
            res = self.send_command(command)
            log.logd(_("Sent get camera frame size command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"PHD2 get_camera_frame_size error : {res.get('error')}"))
            return log.return_error(_("PHD2 get_camera_frame_size error"),{"error":res.get('error')})
        log.logd(_("PHD2 get_camera_frame_size successfully"))
        result = res.get('result')
        log.logd(_(f"Current camera frame : [{result[0]},{result[1]}]"))
        return log.return_success(_("PHD2 get_camera_frame_size successfully"),{"width":result[0],"height":result[1]})

    def _get_calibrated(self) -> dict:
        """
            Get if calibrated | 获取校准状态
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        log.logd(_("Trying to get calibrated status ... "))
        command = self.generate_command("get_calibrated")
        try:
            res = self.send_command(command)
            log.logd(_("Sent get calibrated command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"PHD2 get_calibrated error : {res.get('error')}"))
            return log.return_error(_("PHD2 get_calibrated error"),{"error":res.get('error')})
        result = res.get('result')
        self.info._is_calibrated = result
        log.logd(_(f"PHD2 get_calibrated successfully , current state : {result}"))
        return log.return_success(_("PHD2 get_calibrated successfully"),{"status":result})

    def _get_calibration_data(self, params : dict) -> dict:
        """
            Get calibration data | 获取校准数据
            Args:
                params : {
                    "type" : str # "AO" or "Mount" , default is "Mount"
                }
            Returns:{
                "status" : int,
                "message" : str
                "params" : dict
            }
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        if not self.info._is_calibrated:
            log.logw(_("It seems that guider not calibrated , check again"))
            res = self._get_calibrated()
            if res.get("status") != 0:
                return
            if res.get("params").get("status") is True:
                self.info._is_calibrated = True
        _type = params.get("type")
        if _type is not None and isinstance(_type,str):
            if _type.upper() not in ["AO","MOUNT"]:
                log.logw(_("Unknown type of calibration data is not supported"))
                _type = "Mount"
        command = self.generate_command("get_calibration_data",_type)
        try:
            res = self.send_command(command)
            log.logd(_("Sent get calibration data command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"PHD2 get_calibration_data error : {res.get('error')}"))
            return log.return_error(_("PHD2 get_calibration_data error"),{"error":res.get('error')})
        result = res.get('result')
        """
            Data example:{
                "calibrated":true,
                "xAngle":-167.1,
                "xRate":39.124,
                "xParity":"-",
                "yAngle":106.1,
                "yRate":39.330,
                "yParity":"+"
            }
        """
        self.info._is_calibrated = result.get("calibrated")

        self.info.c_status._model.xAngle = result.get("xAngle")
        log.logd(_(f"Calibrating model xAngle : {self.info.c_status._model.xAngle}"))
        self.info.c_status._model.xRate = result.get("xRate")
        log.logd(_(f"Calibrating model xRate : {self.info.c_status._model.xRate}"))
        self.info.c_status._model.xParity = result.get("xParity")
        log.logd(_(f"Calibrating model xParity : {self.info.c_status._model.xParity}"))

        self.info.c_status._model.yAngle = result.get("yAngle")
        log.logd(_(f"Calibrating model yAngle : {self.info.c_status._model.yAngle}"))
        self.info.c_status._model.yRate = result.get("yRate")
        log.logd(_(f"Calibrating model yRate : {self.info.c_status._model.yRate}"))
        self.info.c_status._model.yParity = result.get("yParity")
        log.logd(_(f"Calibrating model yParity : {self.info.c_status._model.yParity}"))

        log.log(_("Get calibration model successfully"))
        return log.return_success(_("Get calibration model successfully"),{"model":self.info.c_status._model.get_dict()})

    def _get_connected(self) -> dict:
        """
            Get if connected | 获取设备是否连接成功
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : This function is to check if the equipment is connected
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        command = self.generate_command("get_connected")
        try:
            res = self.send_command(command)
            log.logd(_("Sent get connected command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"PHD2 get_connected error : {res.get('error')}"))
            return log.return_error(_("PHD2 get_connected error"),{"error":res.get('error')})
        result = res.get("result")
        self.info._is_device_connected = result
        log.logd(_(f"Current device connected status : {result}"))
        log.log(_("Get device status successfully"))
        return log.return_success(_("Get device status successfully"),{"status":result})

    def _get_cooler_status(self) -> dict:
        """
            Get cooler status | 获取制冷状态
            Args: None
            Returns:{
                "status" : int,
                "message" : str
                "params" : dict
            }
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        command = self.generate_command("get_cooler_status")
        try:
            res = self.send_command(command)
            log.logd(_("Sent get cooler status command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"Get cooler status error : {res.get('error')}"))
            self.info._can_cooling = False
            return log.return_error(_("Get cooler status error"),{"error":res.get('error')})
        result = res.get("result")
        """
            Data structure:	
                "temperature": sensor temperature in degrees C (number), 
                "coolerOn": boolean, 
                "setpoint": cooler set-point temperature (number, degrees C), 
                "power": cooler power (number, percent)
        """
        self.info._can_cooling = True
        self.info.cooling_model._is_cooling = result.get("coolerOn")
        log.logd(_(f"Current cooling status : {self.info.cooling_model._is_cooling}"))
        self.info.cooling_model._temperature = result.get("temperature")
        log.logd(_(f"Current camera temperature : {self.info.cooling_model._temperature}"))
        self.info.cooling_model._target_temperature = result.get("setpoint")
        log.logd(_(f"Target temperature : {self.info.cooling_model._target_temperature}"))
        self.info.cooling_model._cooling_power = result.get("power")
        log.logd(_(f"Current cooling power : {self.info.cooling_model._cooling_power}"))

        log.log(_("Get camera cooling status successfully"))
        return log.return_success(_("Get camera cooling status successfully"),{"status":result})

    def _get_current_equipment(self) -> dict:
        """
            Get current equipment | 获取当前设备
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : 	This function may be called multiple times
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        command = self.generate_command("get_current_equipment")
        try:
            res = self.send_command(command)
            log.logd(_("Sent get current equipment command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"Get current camera information error: {res.get('error')}"))
            return log.return_error(_("Get current camera information error"),{"error":res.get('error')})
        """
            Data example:
                example: {
                    "camera":{
                        "name":"Simulator",
                        "connected":true
                    },
                    "mount":{
                        "name":"On Camera",
                        "connected":true
                    },
                    "aux_mount":{
                        "name":"Simulator",
                        "connected":true
                    },
                    "AO":{
                        "name":"AO-Simulator",
                        "connected":false
                    },
                    "rotator":{
                        "name":"Rotator Simulator .NET (ASCOM)",
                        "connected":false
                    }
                }
        """
        result = res.get('result')
        _content = None
        for item in ["camera","mount","aux_mount","ao"]:
            exec(f"_content = result.get({item})")
            if _content is not None:
                exec(f"self.info.equipment_model._{item}_name = _content.get('name')")
                log.logd(_(f"Current {item} name : {_content.get('name')}"))
                exec(f"self.info.equipment_model._is_{item}_connected = _content.get('connected')")
                log.logd(_(f"Current {item} connected : {_content.get('connected')}"))
            else:
                exec(f"self.info.equipment_model._{item}_name =''")
                exec(f"self.info.equipment_model._is_{item}_connected = False")

        log.log(_("Get equipment information successfully"))
        return log.return_success(_("Get equipment information successfully"),{"info":result})


    def _get_dec_guide_mode(self) -> dict:
        """
            Get dec_guide_mode | 获取DEC导星模式
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : "Off"/"Auto"/"North"/"South"
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        command = self.generate_command("get_dec_guide_mode")
        try:
            res = self.send_command(command)
            log.logd(_("Sent get dec_guide_mode command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"Get dec_guide_mode error: {res.get('error')}"))
            return log.return_error(_("Get dec_guide_mode error"),{"error":res.get('error')})
        mode = res.get('result')
        log.logd(_(f"Current DEC guiding mode : {mode}"))
        log.log(_("Get DEC guiding mode successfully"))
        return log.return_success(_("Current DEC guiding mode"),{"mode":mode})

    def _get_exposure(self) -> dict:
        """
            Get exposure value in milliseconds | 获取曝光时长
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        command = self.generate_command("get_exposure")
        try:
            res = self.send_command(command)
            log.logd(_("Sent get exposure command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"Get exposure error: {res.get('error')}"))
            return log.return_error(_("Get exposure error"),{"error":res.get('error')})
        exposure = res.get('result')
        self.info.exposure = exposure
        log.logd(_(f"Current exposure value : {exposure}"))
        log.log(_("Get exposure successfully"))
        return log.return_success(_("Current exposure value"),{"exposure":exposure})

    def _get_exposure_durations(self) -> dict:
        """
            Get exposure durations | 获取曝光持续时间
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : array of integers: the list of valid exposure times in milliseconds
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        command = self.generate_command("get_exposure_durations")
        try:
            res = self.send_command(command)
            log.logd(_("Sent get exposure durations command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"Get exposure duration error: {res.get('error')}"))
            return log.return_error(_("Get exposure duration error"),{"error":res.get('error')})
        exposure_durations = res.get('result')
        self.info.exposure_durations = exposure_durations
        log.logd(_(f"Current exposure durations : {exposure_durations}"))
        log.log(_("Get exposure durations successfully"))
        return log.return_success(_("Current exposure durations"),{"exposure_durations":exposure_durations})

    def _get_guide_output_enabled(self) -> dict:
        """
            Get guide output enabled | 获取是否允许导星输出
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : boolean: true when guide output is enabled
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        command = self.generate_command("get_guide_output_enabled")
        try:
            res = self.send_command(command)
            log.logd(_("Sent get guide output enabled command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"Get guide output enabled error: {res.get('error')}"))
            return log.return_error(_("Get guide output enabled error"),{"error":res.get('error')})
        guide_output_enabled = res.get('result')
        self.info.g_status._output_enabled = guide_output_enabled
        log.logd(_(f"Current guide output enabled : {guide_output_enabled}"))
        log.log(_("Get guide output enabled status successfully"))
        return log.return_success(_("Current guide output enabled"),{"enabled":guide_output_enabled})

    def _get_lock_position(self) -> dict:
        """
            Get lock position | 获取锁定位置
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : array: [x, y] coordinates of lock position, or null if lock position is not set
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        command = self.generate_command("get_lock_position")
        try:
            res = self.send_command(command)
            log.logd(_("Sent get lock position command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"Get lock position error: {res.get('error')}"))
            return log.return_error(_("Get lock position error"),{"error":res.get('error')})
        lock_position = res.get('result')
        self.info._lock_position_x = lock_position[0]
        self.info._lock_position_y = lock_position[1]
        log.logd(_(f"Current lock position : {lock_position}"))
        log.log(_("Get lock position successfully"))
        return log.return_success(_("Current lock position"),{"position":lock_position})

    def _get_lock_shift_enabled(self) -> dict:
        """
            Get lock shift enabled | 获取是否允许锁定后强制校准
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : boolean: true if lock shift enabled
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        command = self.generate_command("get_lock_shift_enabled")
        try:
            res = self.send_command(command)
            log.logd(_("Sent get lock shift enabled command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"Get lock shift enabled error: {res.get('error')}"))
            return log.return_error(_("Get lock shift enabled error"),{"error":res.get('error')})
        lock_shift_enabled = res.get('result')
        self.info._lock_shift_enabled = lock_shift_enabled

    def _get_lock_shift_params(self) -> dict:
        """
            Get lock shift params | 获取锁定后强制配置
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : example: {"enabled":true,"rate":[1.10,4.50],"units":"arcsec/hr","axes":"RA/Dec"}
        """

    def _get_paused(self) -> dict:
        """
            Get paused | 获取是否暂停
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : boolean: true if paused
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        command = self.generate_command("get_paused")
        try:
            res = self.send_command(command)
            log.logd(_("Sent get paused command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"Get paused error: {res.get('error')}"))
            return log.return_error(_("Get paused error"),{"error":res.get('error')})
        self.info._is_guiding = False
        log.log(_("Guiding is paused"))
        return log.return_success(_("Guiding is paused"),{})

    def _get_pixel_scale(self) -> dict:
        """
            Get the pixel scale of the current image 
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : number: guider image scale in arc-sec/pixel.
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        command = self.generate_command("get_pixel_scale")
        try:
            res = self.send_command(command)
            log.logd(_("Sent get pixel scale command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"Get pixel scale error: {res.get('error')}"))
            return log.return_error(_("Get pixel scale error"),{"error":res.get('error')})
        self.info.g_status._pixel_scale = res.get("result")
        log.logd(_(f"Current pixel scale : {res.get('result')}"))
        return log.return_success(_("Current pixel scale"),{"value":res.get("result")})

    def _get_profile(self) -> dict:
        """
            Get the profile | 获取配置文件
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : {"id":profile_id,"name":"profile_name"}
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        command = self.generate_command("get_profile")
        try:
            res = self.send_command(command)
            log.logd(_("Sent get profile command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"Get profile error: {res.get('error')}"))
            return log.return_error(_("Get profile error"),{"error":res.get('error')})
        self.info._profile = res.get("result")
        log.logd(_(f"Current profile : {res.get('result')}"))
        return log.return_success(_("Get profile"),{"profile":res.get('result')})

    def _get_profiles(self) -> dict:
        """
            Get the profiles | 获取配置文件
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : array of {"id":profile_id,"name":"profile_name"}	
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        command = self.generate_command("get_profiles")
        try:
            res = self.send_command(command)
            log.logd(_("Sent get profiles command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"Get profiles error: {res.get('error')}"))
            return log.return_error(_("Get profiles error"),{"error":res.get('error')})
        self.info._profiles = res.get("result")
        log.logd(_(f"Current profiles : {res.get('result')}"))
        return log.return_success(_("Get profiles"),{"profiles":res.get('result')})

    def _get_search_region(self) -> dict:
        """
            Get the search region | 获取搜索范围
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : integer: search region radius
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        command = self.generate_command("get_search_region")
        try:
            res = self.send_command(command)
            log.logd(_("Sent get search region command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"Get search region error: {res.get('error')}"))
            return log.return_error(_("Get search region error"),{"error":res.get('error')})
        self.info.g_status._search_region = res.get('result')
        log.logd(_(f"Current search region : {res.get('result')}"))
        return log.return_success(_("Get search region"),{"search_region":res.get('result')})

    def _get_ccd_temperature(self) -> dict:
        """
            Get the ccd temperature | 获取温度
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : "temperature": sensor temperature in degrees C (number)	
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        command = self.generate_command("get_ccd_temperature")
        try:
            res = self.send_command(command)
            log.logd(_("Sent get ccd temperature command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"Get ccd temperature error: {res.get('error')}"))
            return log.return_error(_("Get ccd temperature error"),{"error":res.get('error')})
        self.info.cooling_model._temperature = res.get('result')
        log.logd(_(f"Current ccd temperature : {res.get('result')}"))
        return log.return_success(_("Get ccd temperature"),{"temperature":res.get('result')})

    def _get_star_image(self) -> dict:
        """
            Get the star image | 获取导星图像
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : This function returns full image !
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        command = self.generate_command("get_star_image")
        try:
            res = self.send_command(command)
            log.logd(_("Sent get star image command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"Get star image error: {res.get('error')}"))
            return log.return_error(_("Get star image error"),{"error":res.get('error')})
        """
            Data structure:
                frame: the frame number, 
                width: the width of the image (pixels), 
                height: height of the image (pixels), 
                star_pos: the star centroid position within the image, 
                pixels: the image data, 16 bits per pixel, row-major order, base64 encoded
        """
        image = res.get('result')
        self.info.image._frame = image.get('frame')
        log.logd(_("Current image frame : {self.info.image._frame}"))
        self.info.image._width = image.get('width')
        log.logd(_("Current image width : {self.info.image._width}"))
        self.info.image._height = image.get('height')
        log.logd(_("Current image height : {self.info.image._height}"))
        self.info.image._star_pos = image.get('star_pos')
        log.logd(_("Current star position of the image : {self.info.image._star_pos}"))
        self.info.image._pixels = image.get('pixels')

        return log.return_success(_("Get star image"),{"image":image})

    def _get_use_subframes(self) -> dict:
        """
            Get the use subframes | 获取是否使用子画幅
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        command = self.generate_command("get_use_subframes")
        try:
            res = self.send_command(command)
            log.logd(_("Sent get use subframes command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"Get use subframes error: {res.get('error')}"))
            return log.return_error(_("Get use subframes error"),{"error":res.get('error')})
        
    def _guide(self,params : dict) -> dict:
        """
            Start guiding | 开导
            Args:
                params : {
                    "settle" : {
                        "pixels" : float,
                        "time" : float
                        "timeout" : float
                    }
                    "recalibrate" bool # default is False
                    "roi" : [x,y,width,height] # default is full frame
                }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        if self.info._is_calibrating:
            log.logw(_("PHD2 server is calibrating now"))
            return log.return_warning(_("PHD2 server is calibrating now"),{})
        if self.info._is_guiding:
            log.logw(_("PHD2 server is already started guiding"))
            return log.return_warning(_("PHD2 server is already started guiding"),{})
        # Check if the parameters are correct
        settle = SettleParams()
        if params.get('settle') is not None:
            settle.pixels = params.get('settle').get('pixels')
            settle.time = params.get('settle').get('time')
            settle.timeout = params.get('settle').get('timeout')
        recalibrate = params.get('recalibrate',False)
        roi = params.get('roi')
        if roi is None:
            roi = [0,0,self.info._width,self.info._height]
        _params = {
            "settle" : settle,
            "recalibrate" : recalibrate,
            "roi" : roi
        }
        command = self.generate_command("guide",_params)
        try:
            res = self.send_command(command)
            log.logd(_("Sent guide command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"Guide error: {res.get('error')}"))
            return log.return_error(_("Guide error"),{"error":res.get('error')})
        self.info._is_guiding = True

    def _guide_pulse(self,params : dict) -> dict:
        """
            Start guiding | 开导
            Args:
                params : {
                    "amount" : int # pulse duration in milliseconds, or ao step count
                    "direction" :str # ("N"/"S"/"E"/"W"/"Up"/"Down"/"Left"/"Right")
                    "equipment" : str # ("AO" or "Mount")
                }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        command = self.generate_command("guide_pulse")
        try:
            res = self.send_command(command)
            log.logd(_("Sent guide pulse command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"Guide pulse error: {res.get('error')}"))
            return log.return_error(_("Guide pulse error"),{"error":res.get('error')})

    def _loop(self) -> dict:
        """
            Start loop | 开始循环曝光
            Args:
                None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : 	start capturing, or, if guiding, stop guiding but continue capturing
        """
        if not self.info._is_connected:
            log.loge(_("PHD2 server is not connected"))
            return log.return_error(_("PHD2 server is not connected"),{})
        command = self.generate_command("loop")
        try:
            res = self.send_command(command)
            log.logd(_("Sent loop command to PHD2 server successfully"))
        except socket.error as e:
            log.loge(_(f"Failed to send command to PHD2 server, error : {e}"))
            return log.return_error(_("Failed to send command to PHD2 server"),{"error":e})
        if "error" in res:
            log.loge(_(f"Loop error: {res.get('error')}"))
            return log.return_error(_("Loop error"),{"error":res.get('error')})
        self.info._is_looping = True

    def _save_image(self) -> dict:
        """
            Save the image | 将图像保存
            Args: None
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : 	save the current image. The client should remove the file when done with it.
        """

    def _set_algo_param(self,params : dict) -> dict:
        """
            Set the algorithm parameters | 设置导星算法
            Args:
                params : {
                    "axis" : str
                    "name" : str
                    "value" : float
                }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : set a guide algorithm parameter on an axis
        """

    def _set_connected(self,params : dict) -> dict:
        """
            Set the connected to equipment | 连接设备
            Args:
                params : {
                    "connect" : bool
                }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : 	connect or disconnect all equipment
        """

    def _set_dec_guide_mode(self, params : dict) -> dict:
        """
            Set DEC guide mode | 设置DEC轴导星模式
            Args:
                params : {
                    "mode" : str # "Off"/"Auto"/"North"/"South"
                }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
        """

    def _set_exposure(self, params : dict) -> dict:
        """
            Set exposure value | 设置曝光时间
            Args:
                params : {
                    "exposure" : int # in milliseconds
                }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
        """

    def _set_guide_output_enabled(self, params : dict) -> dict:
        """
            Set the output of the guide | 设置是否允许导星输出
            Args:
                params : {
                    "enable" : bool
                }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : 	Enables or disables guide output
        """

    def _set_lock_position(self , params : dict) -> dict:
        """
            Set star lock position | 设置锁定位置
            Args:
                params : {
                    "X" : float,
                    "Y" : float
                    "EXACT" : bool
                }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : When EXACT is true, the lock position is moved to the exact given coordinates. When false, the current position is moved to the given coordinates and if a guide star is in range, the lock position is set to the coordinates of the guide star.
        """

    def _set_lock_shift_enabled(self , params : dict) -> dict:
        """
            Set lock shift enabled | 设置锁定锁键值
            Args:
                params : {
                    "enable" : bool
                }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
        """

    def _set_lock_shift_params(self,params : dict) -> dict:
        """
            Set lock shift parameters | 设置锁定锁键值
            Args:
                params : {
                    "rate" : [XRATE,YRATE],
                    "units":UNITS,
                    "axes":AXES
                }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : 	UNITS = "arcsec/hr" or "pixels/hr"; AXES = "RA/Dec" or "X/Y"
        """

    def _set_paused(self,params : dict) -> dict:
        """
            Set paused | 暂停
            Args:
                params : {
                    "PAUSED" : bool,
                    "FULL" : str,
                }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : When setting paused to true, an optional second parameter with value "full" can be provided to fully pause phd, including pausing looping exposures. Otherwise, exposures continue to loop, and only guide output is paused. Example: {"method":"set_paused","params":[true,"full"],"id":42}
        """

    def _set_profile(self,params : dict) -> dict:
        """
            Set profile | 设置配置文件
            Args:
                params : {
                    "profile_id" : int
                }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : 	Select an equipment profile. All equipment must be disconnected before switching profiles.
        """

    def _shutdown(self) -> dict:
        """
            Shutdown | 停止
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
        """

    def _stop_capture(self) -> dict:
        """
            Stop capture | 停止拍摄
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
            NOTE : 	Stop capturing (and stop guiding)
        """

    # #########################################################################
    #
    # Overrides BasicGuiderAPI methods
    #
    # #########################################################################

    def start_guiding(self, params: dict) -> dict:
        """
            Start guiding | 开导
            Args:
                params : {
                    
                }
            Returns:{
                "status" : int,
                "message" : str,
                "params" : dict
            }
        """