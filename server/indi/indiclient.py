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

import PyIndi
from server.indi.indidevice import INDIDevice

class INDIClient(PyIndi.BaseClient):
    """
        Basic INDI Client Interface
    """

    def __init__(self,host = "127.0.0.1",port = 7624, callbacks = {},auto_connect = True) -> None:
        """
            Initialize a new INDI client | 初始化一个新的INDI客户端
            Args :
                host : str # host of the INDI server , default is "127.0.0.1"
                port : int # port of the INDI server, default is 7624
                callbacks : dict # callbacks for the INDI server
                auto_connect : bool, default is True
            Return : None
        """
        PyIndi.BaseClient.__init__(self)
        self.host = host
        self.port = port
        self.callbacks = callbacks
        # Set up the INDI client but don't connect
        self.setServer(self.host,self.port)
        # If the auto connect option is enabled
        if auto_connect:
            self.connectServer()

    def get_devices(self) -> list:
        """
            Get a list of all available INDI devices
            Args :
                None
            Return :
                list : list of all available INDI devices
        """
        return [INDIDevice(x, self) for x in self.device_names]

    def get_device_by_interface(self, interface) -> list:
        """
            Get a list of all available INDI devices by interface
            Args :
                interface : str
            Return :
                list : list of all available INDI devices by interface
        """
        return [INDIDevice(x, self) for x in [x.name for x in self.devices() if interface in x.interfaces]]

    @property
    def device_names(self) -> list:
        """
            Get a list of all available INDI device names
            Args :
                None
            Return :
                list : list of all available INDI device names
        """
        return [d.getDeviceName() for d in self.getDevices()]

    def newDevice(self, d) -> None:
        """
            Create a new INDI device
            Args :
                d : INDIDevice
            Return :
                None
        """
        device = INDIDevice(d.getDeviceName(), self)
        self.run_callback('on_new_device', device)

    def removeDevice(self, d) -> None:
        """
            Remove a INDI device
            Args :
                d : INDIDevice
            Return :
                None
        """
        self.run_callback('on_device_removed', d.getDeviceName())

    def newProperty(self, p) -> None:
        """
            Create a new INDI property
            Args :
                p : INDIDevice
            Return :
                None
        """
        self.run_callback('on_new_property', device=p.getDeviceName(), group=p.getGroupName(), property_name=p.getName())

    def removeProperty(self, p) -> None:
        """
            Remove a INDI property
            Args :
                p : INDIDevice
            Return :
                None
        """
        self.run_callback('on_remove_property', p)

    def newBLOB(self, bp) -> None:
        """
            Create a new INDI BLOB
            Args :
                bp : INDIBlob
            Return :
                None
        """
        self.run_callback('on_new_blob', bp)

    def newSwitch(self, svp) -> None:
        """
            Create a new INDI switch
            Args :
                svp : INDISwitch
            Return :
                None
        """
        self.run_callback('on_new_switch', svp)

    def newNumber(self, nvp) -> None:
        """
            Create a new INDI number
            Args :
                nvp : INDINumber
            Return :
                None
        """
        self.run_callback('on_new_number', nvp)

    def newText(self, tvp) -> None:
        """
            Create a new INDI text
            Args :
                tvp : INDIText
            Return :
                None
        """
        self.run_callback('on_new_text', tvp)

    def newLight(self, lvp) -> None:
        """
            Create a new INDI light
            Args :
                lvp : INDILight
            Return :
                None
        """
        self.run_callback('on_new_light', lvp)

    def newMessage(self, d, m) -> None:
        """
            Create a new INDI message
            Args :
                d : INDIDevice
                m : INDIMessage
            Return :
                None
        """
        device = INDIDevice(d.getDeviceName(), self)
        message = device.get_queued_message(m)
        self.run_callback('on_new_message', device, message)

    def serverConnected(self) -> None:
        """
            On server connected
            Args :
                None
            Return :
                None
        """
        self.run_callback('on_server_connected')        

    def serverDisconnected(self, code) -> None:
        """
            On server disconnected
            Args :
                code : int
            Return :
                None
        """
        self.run_callback('on_server_disconnected', code)

    def run_callback(self, name, *args, **kwargs) -> None:
        """
            Run a callback
            Args :
                name : str
                *args : list
                **kwargs : dict
            Return :
                None
        """
        callback = self.callbacks.get(name)
        if callback:
            callback(*args, **kwargs)