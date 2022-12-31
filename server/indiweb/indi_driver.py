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

import os
from utils.lightlog import lightlog
log = lightlog(__name__)

from utils.i18n import _

class INDIDriver(object):
    """
        INDI Driver infomation container
    """

    def __init__(self,name : str,lable : str,version : str,binary : str ,family : str,skeleton = False,custom = False) -> None:
        """
            Initial a INDI infomation container
            Args:
                name : str # name of the driver
                lable : str # name of the lan driver
                version : str # version of the driver
                binary : str # path to the driver binary
                family : str # family of the driver
                skeleton : bool # skeleton of the driver
                custom : bool # whether this is a custom driver
        """
        self.name = name
        self.lable = lable
        self.version = version
        self.binary = binary
        self.family = family
        self.skeleton = skeleton
        self.custom = custom

import xml.etree.ElementTree as ET

INDI_DATA_PATH = "/usr/share/indi/"

class INDIDriverCollection(object):
    """
        INDI Driver infomation container
    """

    def __init__(self , path = INDI_DATA_PATH) -> None:
        """
            Initial a new INDIDriverCollection
            Args:
                path : str # path to the INDI driver data xml files
        """
        if not os.path.exists(path):
            log.loge(_("INDI data folder is not existed"))
        self.path = path
        self.drivers = []
        self.files = []

    def parser_xml(self) -> None:
        """
            Parse INDI driver data xml files
        """
        # Found all of the driver data files
        for f in os.listdir(self.path):
            if f.endswith(".xml") and '_sk' not in f:
                self.files.append(os.path.join(self.path, f))
        # Load all of the drivers data into INDIDriver
        for f in self.files:
            try:
                tree = ET.parse(f)
                root = tree.getroot()

                for group in root.findall('devGroup'):
                    family = group.attrib['group']

                    for device in group.findall('device'):
                        label = device.attrib['label']
                        skel = device.attrib.get('skel', None)
                        drv = device.find('driver')
                        name = drv.attrib['name']
                        binary = drv.text
                        version = device.findtext('version', '0.0')

                        skel_file = os.path.join(self.path, skel) if skel else None
                        driver = INDIDriver(name, label, version,
                                              binary, family, skel_file)
                        self.drivers.append(driver)
            except KeyError as e:
                log.loge("Error in file %s: attribute %s not found" % (f, e))
            except ET.ParseError as e:
                log.loge("Error in file %s: %s" % (f, e))
        # Sort all drivers by label
        self.drivers.sort(key=lambda x: x.label)

    def parser_custom_driver(self,drivers : list) -> None:
        """
            Parser custom driver
        """
        for custom in drivers:
            try:
                driver = INDIDriver(custom['name'], custom['label'], custom['version'], custom['exec'],
                                    custom['family'], None, True)
                self.drivers.append(driver)
            except KeyError as e:
                log.loge("Error in file %s: attribute %s not found" % (custom,e))

    def clear_custom_drivers(self) -> None:
        """
            Clear all custom drivers
        """
        self.drivers = list(filter(lambda driver: driver.custom is not True, self.drivers))

    def get_by_name(self, name) -> INDIDriver | None:
        """
            Get driver by name
            Args:
                name : str # name of the driver
            Returns:
                INDIDriver object
        """
        for driver in self.drivers:
            if driver.name == name:
                return driver
        return None

    def get_by_label(self, label) -> INDIDriver | None:
        """
            Get driver by label
            Args:
                label : str # label of the driver
            Returns:
                INDIDriver object
        """
        for driver in self.drivers:
            if driver.label == label:
                return driver
        return None

    def get_family(self, family) -> dict:
        """
            Get driver family
            Args:
                family : str # family of the driver
            Returns:
                INDIDriver object
        """
        families = {}
        for drv in self.drivers:
            if drv.family in families:
                families[drv.family].append(drv.label)
            else:
                families[drv.family] = [drv.label]
        return families
