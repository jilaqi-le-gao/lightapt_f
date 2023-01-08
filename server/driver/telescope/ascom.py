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

import socket
import requests
from time import sleep

from libs.alpyca.telescope import Telescope
from libs.alpyca.exceptions import (DriverException,
                                        NotConnectedException,
                                        NotImplementedException,
                                        InvalidValueException,
                                        InvalidOperationException)

from server.basic.telescope import BasicTelescopeAPI,BasicTelescopeInfo

from utils.i18n import _
from utils.lightlog import lightlog
logger = lightlog(__name__)

class AscomTelescopeAPI(BasicTelescopeAPI):
    """
        ASCOM Telescope API Interface based on Alpyca.\n
        NOTE : If the return parameters is None , that does not mean there is no error message
    """

    def __init__(self) -> None:
        """
            Initialize a new ASCOM telescope object
            Args : None
            Returns : None
        """
        self.info = BasicTelescopeInfo()
        self.device = None

    def __del__(self) -> None:
        """
            Destory the ASCOM telescope object
            Args : None
            Returns : None
        """
        if self.info._is_connected:
            self.disconnect()

    def __str__(self) -> str:
        """
            Return a string representation of the ASCOM telescope object
            Args : None
            Returns : String
        """
        return """ASCOM Telescope API Interface via Alpyca"""

    def connect(self,params : dict) -> dict:
        """
            Connect to the ASCOM telescope
            Args : 
                params : dict
                    host : str # host of the ASCOM remote server
                    port : int # port of the ASCOM remote server
                    device_number : int # device number of the ASCOM telescope , default is 0
            Returns : dict
                status : int # status of the connection
                message : str # message of the connection
                params : dict
                    info : dict # BasicTelescopeInfo.get_dict()
        """
        if self.info._is_connected or self.device is not None:
            logger.loge(_("Telescope had already connected , please do not connect again"))
            return logger.return_error(_("Telescope has already connected"),{"info":self.info.get_dict()})
        # Get the parameters if parameters is not specified , just use the default parameters
        _host = params.get("host","127.0.0.1")
        _port = params.get("port",11111)
        _device_number = params.get("device_number",0)
        # Trying to connect to ASCOM remote server
        try:
            # Establish connection with ASCOM server
            self.device = Telescope(_host + ":" + _port, _device_number)
            # Make telescope connected
            self.device.Connected = True
        except DriverException as e:
            logger.loge(_("Failed to connect to telescope : {}").format(str(e)))
            return logger.return_error(_("Failed to connect telescope"),{"error": str(e)})
        except ConnectionError as e:
            logger.loge(_("Network error while connecting to telescope : {}").format(str(e)))
            return logger.return_error(_("Network error while connecting to telescope"),{"error": str(e)})

        logger.log(_("Connected to telescope successfully"))
        self.info._is_connected = True
        res = self.get_configration()
        if res.get("status") != 0:
            logger.loge(res.get("message"))
            return logger.return_error(res.get("message"))
        return logger.return_success(res.get("message"),{"info":self.info.get_dict()})

    def disconnect(self) -> dict:
        """
            Disconnect from the ASCOM telescope
            Args : None
            Returns : dict
                status : int # status of the disconnection
                message : str # message of the disconnection
                params : None
        """
        # If the telescope is not connected , do not execute disconnecting command
        if not self.info._is_connected or self.device is None:
            logger.loge(_("Telescope had not connected , please connect before disconnecting"))
            return logger.return_error(_("Telescope has not connected"),{})
        # If the telescope is slewing , stop it before disconnecting
        if self.info._is_slewing:
            logger.logw(_("Telescope is slewing , trying to abort the operation"))
            res = self.abort_goto()
            if res.get("status") != 0:
                logger.loge(res.get("message"))
                return logger.return_error(res.get("message"),{"error":res.get("params",{}).get("error")})
        # Trying to disconnect from the server , however this just destroys the connection not the server
        try:
            self.device.Connected = False
        except DriverException as e:
            logger.loge(_("Failed to disconnect from telescope : {}").format(str(e)))
            return logger.return_error(_("Failed to disconnect telescope"),{"error": str(e)})
        except ConnectionError as e:
            logger.loge(_("Network error while disconnecting from telescope : {}").format(str(e)))
            return logger.return_error(_("Network error while disconnecting from telescope"),{"error":str(e)})
        # If disconnecting from the server succeeded, clear the variables
        self.device = None
        self.info._is_connected = False
        logger.log(_("Disconnected from server successfully"))
        return logger.return_success(_("Disconnected from server successfully"),{})

    def reconnect(self) -> dict:
        """
            Reconnect to the ASCOM telescope
            Args : None
            Returns : dict
                status : int # status of the disconnection
                message : str # message of the disconnection
                params : dict
                    info : dict = self.info.get_dict()
            NOTE : This function is just like a mixing of connect() and disconnect()
        """
        # If the telescope is not connected, do not execute reconnecting command
        if not self.info._is_connected or self.device is None:
            logger.loge(_("Telescope had not connected, please connect before reconnecting"))
            return logger.return_error(_("Telescope has not connected"),{})
        # If the telescope is slewing, stop it before reconnecting
        if self.info._is_slewing:
            logger.logw(_("Telescope is slewing, trying to reconnect"))
            res = self.reconnect_goto()
            if res.get("status")!= 0:
                logger.loge(res.get("message"))
                return logger.return_error(res.get("message"),{"error":res.get("params",{}).get("error")})
        # Trying to reconnect the telescope , but we hope that the server is working properly
        self.info._is_connected = False
        try:
            self.device.Connected = False
            sleep(1)
            self.device.Connected = True
        except DriverException as e:
            logger.loge(_("Failed to reconnect to telescope : {}").format(str(e)))
            return logger.return_error(_("Failed to reconnect telescope"),{"error": str(e)})
        except ConnectionError as e:
            logger.loge(_("Network error while reconnecting to telescope : {}").format(str(e)))
            return logger.return_error(_("Network error while reconnecting to telescope"),{"error":str(e)})
        # Do not forget to set the status
        self.info._is_connected = True
        logger.log(_("Reconnected telescope successfully"))
        return logger.return_success(_("Reconnected telescope successfully"),{"info": self.info.get_dict()})
    
    def scanning(self) -> dict:
        """
            Scanning the telescope one by one tcp connection
            Args : None
            Returns : dict
                status : int # status of the disconnection
                message : str # message of the disconnection
                params : dict
                    telescope : list # a list of telescope found
        """
        # Though this is a little bit strange that if a telescope had already connected,
        # you can not scanning the other telescopes,this is because too many requests may make the server down
        if self.info._is_connected or self.device is not None:
            logger.loge(_("Please disconnect from the telescope before scanning other telescopes"))
            return logger.return_error(_("Telescope has already connected"),{})
        # Scanning is just try a few port the server probably running on , the most reliable port is 11111
        telescope_list = []
        for port in ["11111","33331","12345"]:
            # Trying to bind a socket port , if the port is already uesd it will cause socket.error
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind("127.0.0.1"+int(port))
                s.shutdown(2)
            except socket.error:
                logger.log(_("{}:{} may have a server listening on").format("127.0.0.1", port))
                # Just try if backend of this port is ASCOM Remote Server
                try:
                    self.device = Telescope("127.0.0.1:"+port,0)
                    self.device.Connected = True
                    # Get the telescope's name
                    telescope_list.append(self.device.Name)
                    sleep(0.1)
                    self.device.Connected = False
                except DriverException as e:
                    logger.loge(_("Failed to connect to telescope : {}").format(str(e)))
                except ConnectionError as e:
                    logger.loge(_("Network error while scanning to telescope : {}").format(str(e)))
        # If no telescope is found,just return an error and a empty list
        if len(telescope_list) == 0:
            logger.loge(_("No telescope found"))
            return logger.return_error(_("No telescope found"),{})
        logger.log(_("Found {} telescope , list : {}").format(len(telescope_list),telescope_list))
        return logger.return_success(
            _("Found {} telescope").format(len(telescope_list)),
            {"telescope" : telescope_list})

    def polling(self) -> dict:
        """
            Polling the telescope newest infomation
            Args : None
            Returns : dict
                status : int # status of the disconnection
                message : str # message of the disconnection
                params : dict
                    info : dict # just return self.info.get_dict()
            NOTE : This function will not refresh the infomation of the telescope , 
                    because this will cause a huge lag and waste system usage.
        """
        if not self.info._is_connected or self.device is None:
            logger.loge(_("Telescope is not connected"))
            return logger.return_error(_("Telescope is not connected"),{})
        res = self.info.get_dict()
        logger.logd(_("New telescope information : {}").format(res))
        return logger.return_success(_("Polling teleescope information"),{"info":res})

    def get_configration(self) -> dict:
        """
            Get all of the configurations needed for further processing
            Args : None
            Returns : dict
                status : int # status of the disconnection
                message : str # message of the disconnection
                params : None
        """
        if not self.info._is_connected or self.device is None:
            logger.loge(_("Telescope is not connected"))
            return logger.return_error(_("Telescope is not connected"),{})
        logger.log(_("Trying to get telescope configuration"))
        try:
            # Basic information , all of the telescopes have these
            self.info._name = self.device.Name
            logger.logd(_(f"Telescope name : {self.info._name}"))
            self.info._id = self.device._client_id
            logger.logd(_(f"Telescope ID : {self.info._id}"))
            self.info._description = self.device.Description
            logger.logd(_(f"Telescope description : {self.info._description}"))
            self.info._ipaddress = self.device.address
            logger.logd(_(f"Telescope IP address : {self.info._ipaddress}"))
            self.info._api_version = self.device.api_version
            logger.logd(_(f"Telescope API version : {self.info._api_version}"))

            self.info._can_park = self.device.CanPark
            logger.logd(_(f"Telescope Can Park : {self.info._can_park}"))
            self.info._can_goto = self.device.CanSlew
            logger.logd(_(f"Telescope Can Slew : {self.info._can_goto}"))
            self.info._can_ahort_goto = True
            logger.logd(_("Telescope Can Abort Slew : {}").format(self.info._can_ahort_goto))
            self.info._can_track = self.device.CanSetTracking
            logger.logd(_("Telescope Can Abort Slew : {}").format(self.info._can_track))
            self.info._can_set_track_rate = self.device.CanSetDeclinationRate and self.device.CanSetRightAscensionRate
            logger.logd(_("Telescope Can Set Track Rates : {}").format(self.info._can_set_track_rate))
            self.info._can_set_track_mode = False
            logger.logd(_("Telescope Can Set Track Mode : {}").format(self.info._can_set_track_mode))

        except DriverException as e:
            logger.loge(_("Failed to get telescope configuration : {}").format(str(e)))
            return logger.return_error(_("Failed to get telescope configuration"),{"error":str(e)})