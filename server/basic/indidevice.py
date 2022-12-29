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

from server.basic.device import BasicDeviceAPI

class defSwitch():
    """
        defined switch
        example:
            <defSwitch name="CONNECT" label="Connect">
                On
            </defSwitch>
        value:
            name : string , usually is uppercase
            label : string, 
    """
    def __init__(self, name : str, label : str,value : str) -> None:
        """
            Initialize a new switch
            Args : 
                name : string,
                label : string,
                value : string
            Returns: None
        """
        self.name = name
        self.label = label
        self.value = value

    def get(self) -> dict:
        """
            get the switch value
            Args : 
                None
            Returns:
                value : dict
        """
        return {
            "name": self.name,
            "label": self.label,
            "value": self.value
        }

    def check(self) -> bool:
        """
            Check if the parameters are valid
            Args : None
            Returns : True or False
        """
        if not self.name.isupper():
            return False
        return True

class defSwitchVector():
    """
        defined switch vector
        example:
            <defSwitchVector device="Telescope Simulator" name="CONNECTION" label="Connection"
                group="Main Control" state="Idle" perm="rw" rule="OneOfMany" timeout="60"
                timestamp="2022-12-26T23:27:33">
                <defSwitch name="CONNECT" label="Connect">
                    On
                </defSwitch>
                <defSwitch name="DISCONNECT" label="Disconnect">
                    Off
                </defSwitch>
            </defSwitchVector>
    """
    
    def __init__(self,device : str,) -> None:
        pass
class newSwitchVector():
    """
        new switch vector\n
        example:
            <newSwitchVector device="Telescope Simulator" name="CONNECTION">
                <oneSwitch name="CONNECT">
                    On
                </oneSwitch>
            </newSwitchVector>
        If we send this command to INDI server then the telescope will be connected.
        We will receive a message from the server to reflect the result of the connection.\n
        example:
            <setSwitchVector device="Telescope Simulator" name="CONNECTION" state="Idle" timeout="60" timestamp="2022-12-29T06:45:22">
                <oneSwitch name="CONNECT">
                    On
                </oneSwitch>
                <oneSwitch name="DISCONNECT">
                    Off
                </oneSwitch>
            </setSwitchVector>
    """

    def __init__(self,device : str,name : str,switch,value : bool) -> None:
        """
            Initialize a new SwitchVector
            Args:
                device (str): device name
                name (str): name of the switch
                switch (str) : switch name
                value (bool): value of the switch, true is "On" and false is "Off"
        """
        self.device = device
        self.name = name
        self.switch = switch
        self.value = value

    def get(self) -> str:
        """
            Generate command string for the switch
            Args:
                None
            Returns:
                str: command string , just like the example
        """
        return """
            <newSwitchVector device="{}" name="{}">
                <oneSwitch name="{}">
                    {}
                </oneSwitch>
            </newSwitchVector>
            """.format(self.device, self.name, self.switch, "On" if self.value else "Off").replace("\n", "")

    def check(self) -> bool:
        """
            Check if the parameters are valid
            Args:
                None
            Returns:
                bool: True if the parameters are valid
        """
        # All INDI switch's name are uppercase letters
        if not self.name.isupper() or not self.switch.isupper() or not isinstance(self.value,bool):
            return False
        return True

class BasicINDIAPI(BasicDeviceAPI):
    """
        Basic INDI client API
    """