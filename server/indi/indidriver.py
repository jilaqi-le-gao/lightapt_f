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
import xml.etree.ElementTree as ET

import server.config as c

from utils.lightlog import lightlog
log = lightlog(__name__)

class DeviceDriver:
    """Device driver container"""

    def __init__(self, name, label, version, binary, family, skel=None, custom=False):
        self.name = name
        self.label = label
        self.skeleton = skel
        self.version = version
        self.binary = binary
        self.family = family
        self.custom = custom


class DriverCollection:
    """A collection of drivers"""

    def __init__(self, path = c.config["indiweb"]["data"]) -> None:
        """
            Initialize the driver collection
            Args:
                path : str # The path to the INDi data directory
            Retruns : None
        """
        self.path = path
        self.drivers = []
        self.files = []
        self.parse_drivers()

    def parse_drivers(self) -> None:
        """
            Parse the INDI drivers
            Args:
                None
            Retruns : None
        """
        for fname in os.listdir(self.path):
            # Skip Skeleton files
            if fname.endswith('.xml') and '_sk' not in fname:
                self.files.append(os.path.join(self.path, fname))

        for fname in self.files:
            try:
                tree = ET.parse(fname)
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
                        driver = DeviceDriver(name, label, version,
                                              binary, family, skel_file)
                        self.drivers.append(driver)

            except KeyError as e:
                log.loge("Error in file %s: attribute %s not found" % (fname, e))
            except ET.ParseError as e:
                log.loge("Error in file %s: %s" % (fname, e))

        # Sort all drivers by label
        self.drivers.sort(key=lambda x: x.label)

    def parse_custom_drivers(self, drivers : list) -> None:
        """
            Parse custom drivers
            Args:
                drivers : list of str
            Retruns : None
        """
        for custom in drivers:
            driver = DeviceDriver(custom['name'], custom['label'], custom['version'], custom['exec'],
                                  custom['family'], None, True)
            self.drivers.append(driver)

    def clear_custom_drivers(self) -> None:
        """
            Clear custom drivers
            Args:
                None
            Retruns : None
        """
        self.drivers = list(filter(lambda driver: driver.custom is not True, self.drivers))

    def by_label(self, label : str) -> str | None:
        """
            Get the driver by label
            Args:
                label : str
            Retruns : str | None
        """
        for driver in self.drivers:
            if driver.label == label:
                return driver
        return None

    def by_name(self, name : str) -> str | None:
        """
            Get the driver by name
            Args:
                name : str
            Retruns : str | None
        """
        for driver in self.drivers:
            if driver.name == name:
                return driver
        return None

    def by_binary(self, binary : str) -> str | None:
        """
            Get the driver by binary
            Args:
                binary : str
            Retruns : str | None
        """
        for driver in self.drivers:
            if (driver.binary == binary):
                return driver
        return None

    def get_families(self) -> dict:
        """
            Get the families
            Args:
                None
            Retruns : dict
        """
        families = {}
        for drv in self.drivers:
            if drv.family in families:
                families[drv.family].append(drv.label)
            else:
                families[drv.family] = [drv.label]
        return families
