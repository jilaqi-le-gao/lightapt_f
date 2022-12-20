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
import threading

class PHD2ClientInfo(BasicGuiderInfo):
    """
        PHD2 client information container
    """

    version : str
    subversion : str
    msgversion : str
    state : str

    mount : str

    _lock_position_x : int
    _lock_position_y : int
    
    calibrate_direction : str   # calibration direction (phase)
    calibrate_distance : float  # distance from starting location
    calibrate_dx : float    # x offset from starting position
    calibrate_dy : float    # y offset from starting position
    calibrate_position = [] # star coordinates
    calibrate_step : int # step number
    calibrate_state : str   # calibration status message

    star_selected_x : int   # lock position X-coordinate
    star_selected_y : int # lock position Y-coordinate

    settle_distance : float # the current distance between the guide star and lock position
    
    guiding_frame : int # The frame number; starts at 1 each time guiding starts
    guiding_time : int # the time in seconds, including fractional seconds, since guiding started
    guiding_dx : float # the X-offset in pixels
    guiding_dy : float # the Y-offset in pixels
    guiding_ra_raw_distance : float # the RA distance in pixels of the guide offset vector
    guiding_dec_raw_distance : float # the DEC distance in pixels of the guide offset vector
    guiding_ra_distance : float # the guide algorithm-modified RA distance in pixels of the guide offset vector
    guiding_dec_distance : float # the guide algorithm-modified DEC distance in pixels of the guide offset vector
    guiding_ra_duration : float # the RA guide pulse duration in milliseconds
    guiding_dec_distance : float # the DEC guide pulse duration in milliseconds
    guiding_ra_direction : str # "East" or "West"
    guiding_dec_direction : str # "North" or "South"
    guiding_starmass : float # the Star Mass value of the guide star
    guiding_snr : float # the computed Signal-to-noise ratio of the guide star
    guiding_hfd : float # the guide star half-flux diameter (HFD) in pixels
    guiding_average_distance : float # 	a smoothed average of the guide distance in pixels
    guiding_ra_limited : bool # true if step was limited by the Max RA setting (attribute omitted if step was not limited)
    guiding_dec_limited : bool # true if step was limited by the Max DEC setting (attribute omitted if step was not limited)

    dither_dx : float # the dither X-offset in pixels
    dither_dy : float # the dither Y-offset in pixels

class PHD2Client(BasicGuiderAPI):
    """
        PHD2 client based on TCP/IP connection
    """

    def __init__(self) -> None:
        self.conn = TcpSocket()
        self.terminate = False
        self._background_task = None
        self.info = PHD2ClientInfo()

    def __del__(self) -> None:
        if self.info._is_guiding:
            self.abort_guiding()
        if self.info._is_connected:
            self.disconnect()

    def connect(self, params: dict) -> dict:
        """
            Connect to PHD2 | 连接PHD2
            Args: 
                params:{
                    "host": str,
                    "port": int
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
            self._background_task = threading.Thread(target=self.background_task)
            self._background_task.start()
        except OSError as e:
            log.loge(_("Failed to connect to PHD2 server"))
            return log.return_error(_("Failed to connect to PHD2 server"),{"error" :e})

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
        message = params.get('message')

        event = message.get('event')

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
                break
            if case("CalibrationDataFlipped"):
                break
            if case("LockPositionShiftLimitReached"):
                break
            if case("LoopingExposures"):
                break
            if case("LoopingExposuresStopped"):
                break
            if case("SettleBegin"):
                break
            if case("Settling"):
                break
            if case("SettleDone"):
                break
            if case("StarLost"):
                break
            if case("GuidingStopped"):
                break
            if case("Resumed"):
                break
            if case("GuideStep"):
                break
            if case("GuidingDithered"):
                break
            if case("LockPositionLost"):
                break
            if case("Alert"):
                break
            if case("GuideParamChange"):
                break
            if case("ConfigurationChange"):
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
        self.info.calibrate_direction = message.get("dir")
        log.logd(_(f"Star calibrating direction : {self.info._calibrating}"))
        self.info.calibrate_distance = message.get("dist")
        log.logd(_(f"Star calibrating distance : {self.info.calibrate_distance}"))
        self.info.calibrate_dx = message.get("dx")
        log.logd(_(f"Star calibrating dx : {self.info.calibrate_dx}"))
        self.info.calibrate_dy = message.get("dy")
        log.logd(_(f"Star calibrating dy : {self.info.calibrate_dy}"))
        self.info.calibrate_position = message.get("pos")
        log.logd(_(f"Star calibrating position : {self.info.calibrate_position}"))
        self.info.calibrate_step = message.get("step")
        log.logd(_(f"Star calibrating step : {self.info.calibrate_step}"))
        self.info.calibrate_state = message.get("State")
        log.logd(_(f"Star calibrating state : {self.info.calibrate_state}"))

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