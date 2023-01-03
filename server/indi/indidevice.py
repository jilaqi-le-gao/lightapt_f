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

import ctypes
import time
from utils.lightlog import lightlog
log = lightlog(__name__)
from utils.i18n import _

import PyIndi

class INDIDevice():
    """
        Basic INDI Device Interface
    """

    timeout = 30

    def __init__(self , device_name : str , indi_client) -> None:
        """
            Initialize the INDI Device | 初始化INID设备
            Args : 
                device_name : str # name of the device
                indi_client : INDIClient
            Returns : None
        """
        self.device_name = device_name
        self.indi_client = indi_client
        self.device = None

    def connect(self) -> dict:
        """
            Connect to the INDI Device | 连接INDI设备
            Args : None
            Returns : dict
        """
        if self.is_connected:
            log.logw(_("Device had already connected , please do not connect again"))
            return log.return_error(_("Device has already connected"),{})
        

    def scanning(self) -> None:
        """
            Scan the INDI device | 扫描INDI设备
            Args : None
            Returns : None
        """
        # If the device is not found, there is looping
        while not self.device:
            self.device = self.indi_client.getDevice(self.name)

    def get_control(self,name : str , control_type : str , timeout = timeout) -> dict | None:
        """
            Get the value of the control | 返回值
            Args : 
                name : str # name of the control
                control_type : str # type of the control
                timeout : int # timeout
            Returns : 
                dict | None
        """
        control = None
        attr = {
            'number': 'getNumber',
            'switch': 'getSwitch',
            'text': 'getText',
            'light': 'getLight',
            'blob': 'getBLOB'
        }[control_type]
        started = time.time()
        while not control:
            control = getattr(self.device, attr)(name)
            if not control and 0 < timeout < time.time() - started:
                log.loge(_("Timeout waiting for finding control : {}").format(name))
                return
            time.sleep(0.01)
        return control

    def has_control(self, name : str, control_type : str) -> bool:
        """
            Check if the device has the control
            Args : 
                name : str # name of the control
                control_type : str # type of the control
            Returns : 
                bool
        """
        if self.get_control(name,control_type,timeout=0.1):
            return True
        return False

    def values(self, control_name : str, control_type : str) -> dict:
        """
            Get the value of the control
            Args : 
                control_name : str # name of the control
                control_type : str # type of the control
            Returns : 
                dict
        """
        return dict(map(lambda c: (c.name, c.value), self.get_control(control_name, control_type)))
       
    def switch_values(self, name : str , control = None) -> list:
        """
            Get the value of the switch control
            Args : 
                name : str # name of the control
                control : dict | None
            Returns : list
        """
        return self.control2dict(name, 'switch', lambda c: {'value': c.s == PyIndi.ISS_ON}, control)

    def text_values(self, name : str , control = None) -> list:
        """
            Get the value of the text control
            Args : 
                name : str # name of the control
                control : dict | None
            Returns : list
        """
        return self.control2dict(name, 'text', lambda c: {'value': c.text}, control)

    def number_values(self, name : str, control = None):
        """
            Get the value of the number control
            Args : 
                name : str # name of the control
                control : dict | None
            Returns : list
        """
        return self.control2dict(name, 'text', lambda c: {'value': c.value, 'min': c.min, 'max': c.max, 'step': c.step, 'format': c.format}, control)

    def light_values(self, name : str , control = None):
        """
            Get the value of the light control
            Args : 
                name : str # name of the control
                control : dict | None
            Returns : list
        """
        return self.control2dict(name, 'light', lambda c: {'value': self.__state_to_str[c.s]}, control)


    def control2dict(self, control_name, control_type, transform, control = None):
        def get_dict(element):
            dest = {'name': element.name, 'label': element.label}
            dest.update(transform(element))
            return dest

        control = control if control else self.get_control(control_name, control_type)
        return [ get_dict(c) for c in control]

    def set_switch(self, name : str , on = [] , off = [] ,sync = True, timeout = timeout) -> dict:
        """
            Set switch on/off
            Args : 
                name : str # The name of the switch
                on : list # The list of switches to switch on
                off : list # The list of switches to switch off
                sync : bool # Whether to sync the switch
                timeout : int # The timeout
            Returns : dict
        """
        control = self.get_control(name, 'switch')
        # Judge whether it is unique
        is_exclusive = control.r == PyIndi.ISR_ATMOST1 or control.r == PyIndi.ISR_1OFMANY
        # If the switch is exclusive
        if is_exclusive :
            on_switches = on_switches[0]
            off_switches = [s.name for s in control if s.name not in on_switches]
        for index in control:
            current_state = index.s
            new_state = current_state
            if index.name in on_switches:
                new_state = PyIndi.ISS_ON
            elif is_exclusive or index.name in off_switches:
                new_state = PyIndi.ISS_OFF
            index.s = new_state
        self.indi_client.sendNewSwitch(control)
        # If the sync mode is enabled
        if sync:
            self.wait_for_control_status(control, statuses=[PyIndi.IPS_IDLE, PyIndi.IPS_OK], timeout=timeout)
        return control

    def set_number(self, name : str, values : dict, sync = True, timeout = timeout) -> dict:
        """
            Set number
            Args : 
                name : str # The name of the number to set
                values : dict # The value of the numer
                sync : bool # Whether to sync the number after setting
                timeout : int # The timeout
            Returns : dict
        """
        control = self.get_control(name, 'number')
        for control_name, index in self.map_indexes(control, values.keys()).items():
            control[index].value = values[control_name]
        self.indi_client.sendNewNumber(control)
        # if sync mode is enabled
        if sync:
            self.__wait_for_control_statuses(control , timeout=timeout)
        return control

    def set_text(self, name : str , values : dict, sync = True, timeout = timeout) -> dict:
        """
            Set text
            Args : 
                name : str # The name of the text to set
                values : dict # The value of the text
                sync : bool # Whether to sync the text after setting
                timeout : int # The timeout
            Returns : dict
        """
        control = self.get_control(control_name, 'text')
        for control_name, index in self.__map_indexes(control, values.keys()).items():
            control[index].text = values[control_name]
        self.indi_client.sendNewText(control)
        # If the sync mode is enabled
        if sync:
            self.__wait_for_control_statuses(control, timeout=timeout)
        return control

    def wait_for_control_statuses(self, control : dict, status = [PyIndi.IPS_OK, PyIndi.IPS_IDLE], timeout = timeout) -> dict | None:
        """
            Wait for control status
            Args : 
                control : dict
                status : list
                timeout : int
            Returns : dict | None
        """
        started = time.time()
        while control.s not in status:
            log.logd(_("{}/{}/{}").format(control.device, control.group, control.name))
            if control.s == PyIndi.IPS_ALERT and 0.5 > time.time() - started:
                log.loge(_("Error while changing property {}").format(control.name))
                return log.loge(_("Error while changing property"),{})
            elapsed = time.time() - started
            if 0 < timeout < elapsed:
                log.loge(_("Timeout error while changing property {}").format(control.name))
                return log.loge(_("Timeout error while changing property"),{"name" : control.name})
            time.sleep(0.01)
        log.logd(_("Sync control changes successfully"))

    def map_indexes(self, control : dict , values) -> dict:
        """
            Map indexes
            Args : 
                control : dict
                values : dict
            Returns : dict
        """
        result = {}
        for i, c in enumerate(control):
             if c.name in values:
                result[c.name] = i
        return result

    def get_properties(self) -> list:
        """
            Get properties
            Returns : list
        """
        properties = self.device.getProperties()
        return [ self.__read_property(p) for p in properties if p]

    def get_property(self, name):
        """
            Get property
            Args : 
                name : str
            Returns : dict
        """
        indi_property = self.device.getProperty(name)
        return self.read_property(indi_property) if indi_property else None

    def get_queued_message(self, index):
        """
            Get queued message
            Args : 
                index : int
            Returns : dict
        """
        return self.device.messageQueue(index)

    def read_property(self, p) -> dict:
        """
            Read property
            Args : 
                p : dict
            Returns : dict
        """
        name = p.getName()
        base_dict = { 
            'name': name, 
            'label': p.getLabel(), 
            'group': p.getGroupName(), 
            'device': p.getDeviceName(), 
            'type': self.__type_to_str[p.getType()], 
            'state': self.__state_to_str[p.getState()]
        }
        permission = p.getPermission()
        base_dict['perm_read'] = permission in [PyIndi.IP_RO, PyIndi.IP_RW]
        base_dict['perm_write'] = permission in [PyIndi.IP_WO, PyIndi.IP_RW]
        control = self.get_control(base_dict['name'], base_dict['type'])

        if p.getType() == PyIndi.INDI_NUMBER:
            base_dict['values'] = self.number_values(name, control)
        elif p.getType() == PyIndi.INDI_SWITCH:
            base_dict['rule'] = self.__switch_types[control.r]
            base_dict['values'] = self.switch_values(name, control)
        elif p.getType() == PyIndi.INDI_TEXT:
            base_dict['values'] = self.text_values(name, control)
        elif p.getType() == PyIndi.INDI_LIGHT:
            base_dict['values'] = self.light_values(name, control)
        return base_dict

    @staticmethod
    def find_interfaces(indidevice) -> list:
        """
            Find interfaces
            Args : 
                indidevice : PyIndi device
            Returns : list
        """
        interface = indidevice.getDriverInterface()
        if type(interface) is int:
            device_interfaces = interface
        else:
            interface.acquire()
            device_interfaces = int(ctypes.cast(interface.__int__(), ctypes.POINTER(ctypes.c_uint16)).contents.value)
            interface.disown()

        interfaces = {
            PyIndi.BaseDevice.GENERAL_INTERFACE: 'general', 
            PyIndi.BaseDevice.TELESCOPE_INTERFACE: 'telescope',
            PyIndi.BaseDevice.CCD_INTERFACE: 'ccd',
            PyIndi.BaseDevice.GUIDER_INTERFACE: 'guider',
            PyIndi.BaseDevice.FOCUSER_INTERFACE: 'focuser',
            PyIndi.BaseDevice.FILTER_INTERFACE: 'filter',
            PyIndi.BaseDevice.DOME_INTERFACE: 'dome',
            PyIndi.BaseDevice.GPS_INTERFACE: 'gps',
            PyIndi.BaseDevice.WEATHER_INTERFACE: 'weather',
            PyIndi.BaseDevice.AO_INTERFACE: 'ao',
            PyIndi.BaseDevice.DUSTCAP_INTERFACE: 'dustcap',
            PyIndi.BaseDevice.LIGHTBOX_INTERFACE: 'lightbox',
            PyIndi.BaseDevice.DETECTOR_INTERFACE: 'detector',
            PyIndi.BaseDevice.ROTATOR_INTERFACE: 'rotator',
            PyIndi.BaseDevice.AUX_INTERFACE: 'aux'
        }
        interfaces = [interfaces[x] for x in interfaces if x & device_interfaces]
        return interfaces