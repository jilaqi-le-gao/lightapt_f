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

from enum import Enum

from gettext import gettext
_ = gettext

class WSCameraError(Enum):
    """
        Regular websocket camera error
    """
    ConnectError = _("Failed to connect to the camera")
    CoolingError = _("Failed to set the cooling temperature and power")

    NotSupportCooling = _("")
    NotSupportTemperatureControl = _("Camera does not support temperature control")
    
    SendStartServer = _("Failed to send message while executing remote_start_server() function")
    SendStopServer = _("Failed to send message while executing remote_stop_server() function")
    SendShutdownServer = _("Failed to send message while executing remote_shutdown_server() function")
    SendDashboardSetup = _("Failed to send message while executing remote_dashboard_setup() function")
    SendConnect = _("Failed to send message while executing remote_connect() function")
    SendDisconnect = _("Failed to send message while executing remote_disconnect() function")
    SendReconnect = _("Failed to send message while executing remote_reconnect() function")
    SendScanning = _("Failed to send message while executing remote_scanning() function")
    SendPolling = _("Failed to send message while executing remote_polling() function")
    SendStartExposure = _("Failed to send message while executing remote_start_exposure() function")
    SendAbortExposure = _("Failed to send message while executing remote_abort_exposure() function")
    SendGetExposureStatus = _("Failed to send message while executing remote_get_exposure_status() function")
    SendGetExposureResult = _("Failed to send message while executing remote_get_exposure_result() function")
    SendStartSequence = _("Failed to send message while executing remote_start_sequence_exposure() function")
    SendAbortSequence = _("Failed to send message while executing remote_abort_sequence_exposure() function")
    SendPauseSequence = _("Failed to send message while executing remote_pause_sequence_exposure() function")
    SendContinueSequence = _("Failed to send message while executing remote_continue_sequence_exposure() function")
    SendGetSequenceExposureStatus = _("Failed to send message while executing remote_get_sequence_status() function")
    SendGetSequenceExposureResults = _("Failed to send message while executing remote_get_sequence_results() function")
    SendCooling = _("Failed to send message while executing remote_cooling() function")
    SendGetCoolingStatus = _("Failed to send message while executing remote_get_cooling_status() function")
    SendGetConfigration = _("Failed to send message while executing remote_get_configuration() function")
    SendSetConfigration = _("Failed to send message while executing remote_set_configuration() function")

class WSCameraSuccess(Enum):
    """
        Regular websocket camera success
    """
    ConnectSuccess = _("Connected to the camera successfully")
    CoolingSuccess = _("Set cooling temperature and power successfully")
    ScanningSuccess = _("Scanning the camera successfully")

class WSCameraWarning(Enum):
    """
        Regular websocket camera warning
    """

class WebAppSuccess(Enum):
    """
        Regular web app success
    """
    DeviceStartedSuccess = _("Started a device server successfully")
    DeviceStoppedSuccess = _("Stopped a device server successfully")
    DeviceRestartSuccess = _("Restarted a device server successfully")

class WebAppError(Enum):
    """
        Regular web app error
    """
    ConfigFileNotFound = _("Could not find configration file ")
    ConfigFolderNotFound = _("Could not find configration folder ")
    ScriptNotFound = _("Could not find script file ")

    EmptyConfigFile = _("Config file is empty ")
    EmptyScriptFile = _("Script file is empty")

    InvalidFile = _("Invalid device configuration file {}")
    InvalidScriptPath = _("Invalid script path ")
    InvalidDeviceType = _("Invalid device type ")
    InvalidDeviceID = _("Invalid device ID")

    LoadConfigFailed = _("Could not load configuration file {}")
    LoadScriptFailed = _("Could not load script file {}")

    HadAlreadyStarted = _("This server has already contained a device ")
    HadAlreadyStartedSame = _("This server has already contained the same device you want to start now ")
    DeviceNotStarted = _("The device you are trying to stop is not available on this server")
    DeviceStopFailed = _("Failed to stop the device")
    DeviceRestartFailed = _("Failed to restart the device")

class WebAppWarning(Enum):
    """
        Regular web app warning
    """
