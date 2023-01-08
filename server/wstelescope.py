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
import threading
from time import sleep
# Third Party Library

# Built-in Library

import server.config as c

from utils.i18n import _
from utils.utility import switch
from utils.lightlog import lightlog
logger = lightlog(__name__)

class ws_telescope(object):
    """
        Websocket Telescope Interface.\n
        Needed Telescope API:
            goto(params : dict) -> dict
                params : 
                    ra : str # format xx:xx:xx.xxx
                    dec : str # format xx:xx:xx.xxx
                    az : str # format xx:xx:xx.xxx
                    alt : str # format xx:xx:xx.xxx
                    j2000 : bool # whether the coordinates is in the format of J2000
            sync(params : dict) -> dict
                params :
                    ra : str # format xx.xx.xx.xxx
                    dec : str # format xx.xx.xx.xxx
                    j2000 : bool # whether the coordinates is in the format of J2000
            move_to(params : dict) -> dict
                params : 
                    direction : str
                    command : str # start or stop
            home() -> dict \n
            park() -> dict \n
            unpark() -> dict \n
            set_park() -> dict \n
            track() -> dict \n
            abort_track() -> dict \n
            set_track_mode() -> dict \n
            set_track_rate() -> dict \n
            get_location() -> dict \n
            update_config() -> dict \n
                NOTE : This function need to get all of the settings of the telescope

        Working methods:
            If a commad is given by client , because all of the functions are non-blocking,
            the function will return immediately.For example, when you try to execute goto command,
            You should call goto() first and then you need to call get_goto_status() while goto process.

            client -> remote_goto() -> goto() -> goto_thread() 
                                                    |
                                                    -> remote_get_goto_status() -> get_goto_status()

        Pay attention to that we must make sure that the command give to telescope is supported.
        Though most of the telescopes support functions like goto,park and home,there are still some
        do not support.So the update_config() must be called when connect to telescope successfully.
    """

    def __init__(self) -> None:
        """
            Initialize the websocket telescope interface object
            Args : None
            Returns : None
        """
        self.device = None
        self.thread = None

    def __del__(self) -> None:
        """
            Close the websocket telescope interface object
            Args : None
            Returns : None
        """
        if self.device.info._is_connected:
            self.device.disconnect()

    def __str__(self) -> str:
        """
            Return the string representation of the websocket telescope interface object
            Args : None
            Returns : Telescope string
        """
        return """
            Basic websocket telescope interface
            version : 1.0.0 indev
        """

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
            Connect to the telescope | 连接望远镜,在成功后获取望远镜信息并返回客户端
            Args : 
                params :
                    "host" : str # default is "localhost"
                    "port" : int # port of the INDI or ASCOM server
                    "type" : str # default is "indi"
                    "name" : str # name of the telescope , default is "CCD Simulator"
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the connection
                id : int # just a random number
                message : str # message of the connection
                params : info : BasicTelescopeInfo object
        """
        _host = params.get("host", "localhost")
        _port = int(params.get("port", 7624))
        _type = params.get("type", "indi")
        _name = params.get("name", "Telescope Simulator")

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
        # If the telescope had already connected
        if self.device.info._is_connected:
            logger.logw(_("Telescope is connected"))
            r["status"] = 2
            r["message"] = "Telescope is connected"
            r["params"]["info"] = self.device.info.get_dict()
            return
        # Check if the type of the telescope is supported
        if _type in ["indi","ascom"]:
            # Connect to ASCOM telescope , the difference between INDI is the devie_number
            if _type == "ascom":    
                from server.driver.telescope.ascom import AscomTelescopeAPI as ascom_telescope
                self.device = ascom_telescope()
                param["device_number"] = 0
            # Connect to INDI telescope , the name of the device is needed
            elif _type == "indi":
                from server.driver.telescope.indi import INDITelescopeAPI as indi_telescope
                self.device = indi_telescope()
                param["name"] = _name
            # Trying to connect the telescope
            res = self.device.connect(params=param)
            if res.get('status') != 0:
                logger.loge(_(f"Failed to connect to {_host}:{_port}, error {res.get('status')}"))
                # If there is no error infomation
                try:
                    r["params"]["error"] = res.get('params').get('error')
                except:
                    pass
            else:
                r["status"] = 0
                r["params"]["info"] = res.get("params").get("info")
            r['message'] = res.get("message")
        # Unkown type of the telescope
        else:
            logger.loge(_(f"Unknown type {_type}"))
            r["message"] = _("Unknown type")
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing connect command"))

    def remote_disconnect(self):
        """
            Disconnect from the telescope
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
        if not self.device.info._is_connected:
            logger.loge(_("Telescope is not connected"))
            r["message"] = _("Telescope is not connected")
        else:
            res = self.device.disconnect()
            if res.get('status')!= 0:
                logger.loge(_(f"Failed to disconnect from the telescope"))
                try:
                    r["params"]["error"] = res.get('params').get('error')
                except:
                    pass
            else:
                r["status"] = 0
                logger.log(_("Disconnected from telescope successfully"))
            r["message"] = res.get('message')
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing disconnect command"))

    def remote_reconnect(self) -> None:
        """
            Reconnect to the telescope
            Args : None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the reconnection
                id : int # just a random number
                message : str # message of the reconnection
                params : info : BasicTelescopeInfo object
        """
        r = {
            "event" : "RemoteReconnect",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        if not self.device.info._is_connected:
            logger.loge(_("Telescope is not connected"))
            r["message"] = _("Telescope is not connected")
        else:
            res = self.device.reconnect()
            if res.get('status')!= 0:
                logger.loge(_(f"Failed to reconnect to the telescope"))
                try:
                    r["params"]["error"] = res.get('params').get('error')
                except:
                    pass
            else:
                r["status"] = 0
                r["params"]["info"] = res.get("params").get("info")
                logger.log(_("Reconnected to telescope successfully"))
            r["message"] = res.get("message")
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing reconnect command"))

    def remote_scanning(self) -> None:
        """
            Scannings from the telescope
            Args : None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the scanning
                id : int # just a random number
                message : str # message of the scanning
                params : list : a list of telescope name
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
            logger.loge(_(f"Failed to scan from the telescope"))
            try:
                r["params"]["error"] = res.get('params').get('error')
                logger.log(_("Error : {}").format(r["params"]["error"]))
            except:
                pass
        else:
            r["status"] = 0
            r["params"]["list"] = res.get("params").get("list")
            logger.log(_("Scanning telescope successfully, found {} telescope").format(len(r["params"]["list"])))
        r["message"] = res.get("message")
    
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing scan command"))

    def remote_polling(self) -> None:
        """
            Polling newest message from the telescope
            Args : None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the polling
                id : int # just a random number
                message : str # message of the polling
                params : dict
                    info : BasicTelescopeInfo object
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
            logger.loge(_(f"Failed to poll from the telescope"))
            try:
                r["params"]["error"] = res.get('params').get('error')
                logger.loge(_("Error : {}").format(r["params"]["error"]))
            except:
                pass
        else:
            r["status"] = 0
            r["params"]["info"] = res.get("params").get("info")
            logger.logd(_("Get telescope information : {}").format(r["params"]["info"]))
        r["message"] = res.get("message")
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing polling command"))

    # #################################################################
    #
    # Telescope control functions
    #
    # #################################################################

    def remote_goto(self,params : dict) -> dict:
        """
            Goto telescope
            Args :
                params : dict
                    ra : str # xx.xx.xx.xxx
                    dec : str # xx.xx.xx.xxx
                    az : str # xx.xx.xx.xxx
                    alt : str # xx.xx.xx.xxx
                    j2000 : bool # J2000 coordinates format
            Returns : dict
            ClientReturn:
                event : str # event name
                status : int # status of the goto operation
                id : int # just a random number
                message : str # message of the goto operation
                params : dict
        """
        r = {
            "event" : "RemoteGoto",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        _ra = params.get("ra")
        _dec = params.get("dec")
        _az = params.get("az")
        _alt = params.get("alt")
        _j2000 = params.get("j2000",False)
        # Check if the parameters are valid and whether telescope is available to goto
        if (_ra is None or _dec is None) and (_az is None or _alt is None):
            logger.loge(_("No coordinates provided"))
            r["message"] = _("No coordinates provided")
        elif not self.device.info._is_connected:
            logger.loge(_("Telescope is not connected"))
            r["message"] = _("Telescope is not connected")
        elif self.device.info._is_slewing:
            logger.loge(_("Telescope is slewing"))
            r["message"] = _("Telescope is slewing , please wait for a moment before continuing")
        elif self.device.info._is_parked:
            logger.loge(_("Telescope is parked"))
            r["message"] = _("Telescope is parked, please unpark telescope before continuing")
        else:
            # If J2000 coordinates are provided , convert them to JNow coordinates
            if _j2000:
                pass
            param = {
                "ra" : _ra,
                "dec" : _dec,
                "az" : _az,
                "alt" : _alt
            }
            res = self.device.goto(param)
            if res.get('status')!= 0:
                logger.loge(_(f"Failed to goto from the telescope"))
                try:
                    r["params"]["error"] = res.get('params').get('error')
                except:
                    pass
            else:
                r["status"] = 0
                self.thread = threading.Thread(target=self.goto_thread)
                self.thread.daemon = True
                self.thread.start()
            r["message"] = res.get('message')    
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing remote goto command"))

    def goto_thread(self) -> None:
        """
            Continue getting goto status and return to client
            Args : None
            Returns : None
        """
        if not self.device.info._is_slewing:
            logger.loge(_("Telescope is not slewing , why will the goto thread start"))
            return
        used_time = 0
        while used_time <= self.device.info.timeout:
            self.remote_get_goto_status()
            sleep(0.5)

    def remote_abort_goto(self) -> None:
        """
            Remote abort goto operation
            Args : None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the aborting operation
                id : int # just a random number
                message : str # message of the aborting operation
                params : dict
            NOTE : This function may still need telescope supported
        """
        r = {
            "event" : "RemoteAbortGoto",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        if not self.device.info._is_connected:
            logger.loge(_("Telescope is not connected"))
            r["message"] = _("Telescope is not connected")
        else:
            if not self.device.info._can_ahort_goto:
                logger.loge(_("Cannot abort goto operation , telescope didn't support"))
                r["message"] = _("Cannot abort goto operation , telescope didn't support")
            else:
                res = self.device.abort_goto()
                if res.get('status')!= 0:
                    logger.loge(_(f"Failed to abort goto operation"))
                    r["message"] = _("Failed to abort goto operation")
                    try:
                        r["params"]["error"] = res.get('params').get('error')
                    except:
                        pass
                else:
                    r["status"] = 0
                    r["message"] = _("Aborted goto operation successfully")
                    logger.log(_("Aborted goto operation successfully"))
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing abort goto command"))

    def remote_get_goto_status(self) -> None:
        """
            Remote get goto status
            Args : None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the goto status
                id : int # just a random number
                message : str # message of the goto status
                params : dict
                    status : int # status of the goto status
        """
        r = {
            "event" : "RemoteGetGotoStatus",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        if not self.device.info._is_connected:
            logger.loge(_("Telescope is not connected"))
            r["message"] = _("Telescope is not connected")
        elif not self.device.info._is_slewing:
            logger.loge(_("Telescope is not slewing"))
            r["message"] = _("Telescope is not slewing")
        else:
            res = self.device.get_goto_status()
            if res.get('status')!= 0:
                logger.loge(_(f"Failed to get goto status"))
                try:
                    r["params"]["error"] = res.get('params').get('error')
                except:
                    pass
            else:
                r["status"] = 0
                r["params"]["status"] = res.get('params').get('status')
            r["message"] = res.get('message')
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing get goto status command"))

    def remote_get_goto_result(self) -> None:
        """
            Remote get goto result
            Args : None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the goto status
                id : int # just a random number
                message : str # message of the goto status
                params : dict
                    ra : str # RA coordinate in JNow format
                    dec : str # DEC coordinate in JNow format
        """
        r = {
            "event" : "RemoteGetGotoResult",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        if not self.device.info._is_connected:
            logger.loge(_("Telescope is not connected"))
            r["message"] = _("Telescope is not connected")
        elif self.device.info._is_slewing:
            logger.loge(_("Telescope is slewing"))
            r["message"] = _("Telescope is slewing")
        else:
            res = self.device.get_goto_result()
            if res.get('status')!= 0:
                logger.loge(_(f"Failed to get goto result"))
                try:
                    r["params"]["error"] = res.get('params').get('error')
                except:
                    pass
            else:
                r["status"] = 0
                try:
                    r["params"]["ra"] = res.get('params').get('ra')
                    r["params"]["dec"] = res.get('params').get('dec')
                except KeyError:
                    logger.loge(_("No final coordinates found"))
            r["message"] = res.get('message')
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing get goto result command"))

    def remote_park(self) -> None:
        """
            Remote park
            Args : None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the goto status
                id : int # just a random number
                message : str # message of the goto status
                params : dict
            NOTE : After this command , you can not goto or change the telescope parameters until you execute the unpark command
        """
        r = {
            "event" : "RemotePark",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        if not self.device.info._is_connected:
            logger.loge(_("Telescope is not connected"))
            r["message"] = _("Telescope is not connected")
        elif self.device.info._is_slewing:
            logger.loge(_("Telescope is slewing"))
            r["message"] = _("Telescope is slewing")
        else:
            res = self.device.park()
            if res.get('status')!= 0:
                logger.loge(_(f"Failed to park"))
                try:
                    r["params"]["error"] = res.get('params').get('error')
                except:
                    pass
            else:
                r["status"] = 0
                self.device.info._is_parked = True
            r["message"] = res.get('message')
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing park command"))

    def remote_unpack(self) -> None:
        """
            Remote unpack
            Args : None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the goto status
                id : int # just a random number
                message : str # message of the goto status
                params : dict
            NOTE : You should call this function to unlock the telescope
        """
        r = {
            "event" : "RemoteUnpack",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        if not self.device.info._is_connected:
            logger.loge(_("Telescope is not connected"))
            r["message"] = _("Telescope is not connected")
        elif not self.device.info._is_parked:
            logger.loge(_("Telescope is not parked"))
            r["message"] = _("Telescope is not parked")
        else:
            res = self.device.unpack()
            if res.get('status')!= 0:
                logger.loge(_(f"Failed to unpack"))
                try:
                    r["params"]["error"] = res.get('params').get('error')
                except:
                    pass
            else:
                r["status"] = 0
            r["message"] = res.get('message')
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing unpark command"))

    def remote_home(self) -> None:
        """
            Remote let telescope go to home position
            Args : None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the goto status
                id : int # just a random number
                message : str # message of the goto status
                params : dict
            NOTE : This function is not like park , after this you can still control the telescope
        """
        r = {
            "event" : "RemoteHome",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        if not self.device.info._is_connected:
            logger.loge(_("Telescope is not connected"))
            r["message"] = _("Telescope is not connected")
        elif self.device.info._is_parked:
            logger.loge(_("Telescope is already parked"))
            r["message"] = _("Telescope is already parked")
        else:
            res = self.device.home()
            if res.get('status')!= 0:
                logger.loge(_(f"Failed to park"))
                try:
                    r["params"]["error"] = res.get('params').get('error')
                except:
                    pass
            else:
                r["status"] = 0
            r["message"] = res.get('message')
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing home command"))

    def remote_set_park_position(self,params : dict) -> None:
        """
            Remote set park position
            Args : 
                params : dict
                    axis1
                    axis2
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the goto status
                id : int # just a random number
                message : str # message of the goto status
                params : dict
            NOTE : This function need telescope supported
        """
        r = {
            "event" : "RemoteSetParkPosition",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        if not self.device.info._is_connected:
            logger.loge(_("Telescope is not connected"))
            r["message"] = _("Telescope is not connected")
        else:
            res = self.device.set_park_position(params)
            if res.get('status')!= 0:
                logger.loge(_(f"Failed to set park position"))
                try:
                    r["params"]["error"] = res.get('params').get('error')
                except:
                    pass
            else:
                r["status"] = 0
            r["message"] = res.get('message')
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing set park position command"))

    def remote_track(self) -> None:
        """
            Remote starting tracking
            Args : None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the goto status
                id : int # just a random number
                message : str # message of the goto status
                params : dict
            NOTE : This function need telescope supported , though I think if a telescope do not support is impossible
        """
        r = {
            "event" : "RemoteTrack",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        if not self.device.info._is_connected:
            logger.loge(_("Telescope is not connected"))
            r["message"] = _("Telescope is not connected")
        elif self.device.info._is_parked:
            logger.loge(_("Telescope is already parked"))
            r["message"] = _("Telescope is already parked")
        elif self.device.info._is_slewing:
            logger.loge(_("Telescope is slewing"))
            r["message"] = _("Telescope is slewing")
        else:
            res = self.device.track()
            if res.get('status')!= 0:
                logger.loge(_(f"Failed to track"))
                try:
                    r["params"]["error"] = res.get('params').get('error')
                except:
                    pass
            else:
                r["status"] = 0
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing track command"))

    def remote_abort_track(self) -> None:
        """
            Remote aborting tracking
            Args : None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the goto status
                id : int # just a random number
                message : str # message of the goto status
                params : dict
        """
        r = {
            "event" : "RemoteAbortTrack",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        if not self.device.info._is_connected:
            logger.loge(_("Telescope is not connected"))
            r["message"] = _("Telescope is not connected")
        elif self.device.info._is_parked:
            logger.loge(_("Telescope is already parked"))
            r["message"] = _("Telescope is already parked")
        elif not self.device.info._is_tracking:
            logger.loge(_("Telescope is not tracking"))
            r["message"] = _("Telescope is not tracking")
        else:
            res = self.device.abort_track()
            if res.get('status')!= 0:
                logger.loge(_(f"Failed to abort track"))
                try:
                    r["params"]["error"] = res.get('params').get('error')
                except:
                    pass
            else:
                r["status"] = 0
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing abort track command"))

    def remote_set_track_rate(self,params : dict) -> None:
        """
            Remote setting track rate
            Args : 
                params : dict
                    ra_rate : float
                    dec_rate : float
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the goto status
                id : int # just a random number
                message : str # message of the goto status
                params : None
        """
        r = {
            "event" : "RemoteSetTrackRate",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : params
        }
        _ra_rate = params.get("ra_rate",self.device.info.track_ra_rate)
        _dec_rate = params.get("dec_rate",self.device.info.track_dec_rate)
        if not self.device.info._is_connected:
            logger.loge(_("Telescope is not connected"))
            r["message"] = _("Telescope is not connected")
        elif self.device.info._is_parked:
            logger.loge(_("Telescope is already parked"))
            r["message"] = _("Telescope is already parked")
        else:
            param = {
                "ra_rate" : _ra_rate,
                "dec_rate" : _dec_rate
            }
            res = self.device.set_track_rate(param)
            if res.get('status')!= 0:
                logger.loge(_(f"Failed to set track rate"))
                try:
                    r["params"]["error"] = res.get('params').get('error')
                except:
                    pass
            else:
                r["status"] = 0
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing set_track_rate command"))

    def remote_set_track_mode(self,params : dict) -> None:
        """
            Remote setting track mode
            Args : 
                params : dict
                    mode : int
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the goto status
                id : int # just a random number
                message : str # message of the goto status
                params : None
        """
        r = {
            "event" : "RemoteSetTrackMode",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : params
        }
        _mode = params.get("mode",self.device.info.track_mode)
        if not self.device.info._is_connected:
            logger.loge(_("Telescope is not connected"))
            r["message"] = _("Telescope is not connected")
        else:
            param = {
                "mode" : _mode
            }
            res = self.device.set_track_mode(param)
            if res.get('status')!= 0:
                logger.loge(_(f"Failed to set track mode"))
                try:
                    r["params"]["error"] = res.get('params').get('error')
                except:
                    pass
            else:
                r["status"] = 0
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing set_track_mode command"))

    def remote_get_location(self) -> None:
        """
            Remote getting location maybe use GPS
            Args : 
                None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the goto status
                id : int # just a random number
                message : str # message of the goto status
                params : 
                    lat : str # latitude of the position
                    lon : str # longitude of the position
        """
        r = {
            "event" : "RemoteGetLocation",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {
                "lat" : 0,
                "lon" : 0
            }
        }
        if not self.device.info._is_connected:
            logger.loge(_("Telescope is not connected"))
            r["message"] = _("Telescope is not connected")
        else:
            res = self.device.get_location()
            if res.get('status')!= 0:
                logger.loge(_(f"Failed to get location"))
                try:
                    r["params"]["error"] = res.get('params').get('error')
                except:
                    pass
            else:
                r["status"] = 0
                try:
                    r["params"]["lat"] = res.get('params').get('lat')
                    r["params"]["lon"] = res.get('params').get('lon')
                except KeyError:
                    logger.loge(_("No location coordinates found"))
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing get_location command"))