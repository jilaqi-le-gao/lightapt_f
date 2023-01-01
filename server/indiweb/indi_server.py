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

from utils.lightlog import lightlog
log = lightlog(__name__)

from utils.i18n import _
from utils.webutils import check_port

import os

try:
    from subprocess import run,check_output
except ImportError:
    log.logw(_("No subprocess module available , will not load indiwebmanager"))

INDI_PORT = 7624
INDI_CONFIG_PATH = os.path.join("/tmp","indi")
INDI_FIFO = os.path.join("/tmp","indiFIFO")

class INDIServerFIFO(object):
    """
        Send commands to INDI server via FIFO pipe.
    """

    def __init__(self,port = INDI_PORT,config_path = INDI_CONFIG_PATH) -> None:
        self.fifo = INDI_FIFO
        self.port = port
        self.config_path = config_path

    def __del__(self) -> None:
        self.stop_server()

    def start_server(self, port = INDI_PORT,drivers=[]) -> None:
        """
            Start a INDI server on the specified port\n
            Args:
                port (int): Port to listen on
            Returns:
                None
            NOTE : This function will just start the server and not start the drivers
        """
        # Check if the server is running or the port is already used
        if self.is_server_running and not check_port():
            log.logw(_("There is a server running on the port you want to start"))
            log.logw(_("We will automatically kill the current server"))
            self.stop_server()
        # Clear the current fifo pipe
        log.log(_("Clearing the current fifo pipe"))
        if run(["rm","-f",self.fifo]).returncode != 0:
            log.logw(_("Failed to clear the current fifo pipe"))
            return
        else:
            log.logw(_("Successfully cleared the current fifo pipe"))
        # Run INDI server with no drivers starting
        cmd = 'indiserver -p {} -m 100 -v -f {} > /tmp/indiserver.log 2>&1 &'.format(self.port, self.fifo)
        log.log(cmd)
        run(cmd, shell=True)

        self.__running_drivers = {}
        for driver in drivers:
            self.start_driver(driver)

    def stop_server(self) -> None:
        """
            Stop the current INDI server\n
            Args:
                None
            Returns:
                None
            NOTE : This function will kill all of the INDI drivers
        """
        log.log(_("Trying to stop the INDI server"))
        cmd = 'killall indiserver'
        if run(cmd,shell=True).returncode != 0:
            log.log(_("Failed to stop the INDI server"))
        else:
            log.log(_("Successfully stopped the INDI server"))

    @property
    def is_server_running(self) -> bool:
        """
            Check if the INDI server is running\n
            Args:
                None
            Returns:
                bool: True if the INDI server is running, False otherwise
            NOTE : This function will return True if the INDI server is running
        """
        if run("ps aux | grep indiserver | grep -v grep",shell=True).returncode != 1:
            return True
        return False

    def start_driver(self,driver : str) -> None:
        """
            Start a new INDI driver\n
            Args:
                driver (str): Name of the driver to start
            Returns:
                None
            NOTE : This function will just start the driver and not start the server
        """
        cmd = 'start %s' % driver.binary
        if driver.skeleton:
            cmd += ' -s "%s"' % driver.skeleton
        cmd = cmd.replace('"', '\\"')
        full_cmd = 'echo "%s" > %s' % (cmd, self.__fifo)
        log.logd(full_cmd)
        run(full_cmd, shell=True)
        self.__running_drivers[driver.label] = driver

    def stop_driver(self,driver : str) -> None:
        """
            Stop the driver 
            Args:
                driver (str): Name of the driver to stop
            Returns:
                None
        """
        cmd = 'stop %s' % driver.binary
        if "@" not in driver.binary:
            cmd += ' -n "%s"' % driver.label
        cmd = cmd.replace('"', '\\"')
        full_cmd = 'echo "%s" > %s' % (cmd, self.__fifo)
        log.logd(full_cmd)
        run(full_cmd, shell=True)
        del self.__running_drivers[driver.label]

    def set_prop(self, dev : str, prop : str, element : str, value : str) -> None:
        """
            Set INDI driver property
            Args:
                dev : str # name of the device
                prop : str # property to set
                element : str # property to set
                value : str # value to set
        """
        cmd = ['indi_setprop', '%s.%s.%s=%s' % (dev, prop, element, value)]
        run(cmd)

    def get_prop(self, dev, prop, element) -> str:
        """
            Get the driver property
            Args:
                dev : str # name of the device
                prop : str # property to get
                element : str # property to get
        """
        cmd = ['indi_getprop', '%s.%s.%s' % (dev, prop, element)]
        output = check_output(cmd)
        return output.split('=')[1].strip()

    def get_state(self, dev, prop) -> str:
        """
            Get the driver state
            Args:
                dev : str # name of the device
                prop : str # property to get
        """
        return self.get_prop(dev, prop, '_STATE')

    def auto_connect(self) -> None:
        """
            Auto connect drivers
            Args : None
            Returns : None
        """
        cmd = ['indi_getprop', '*.CONNECTION.CONNECT']
        output = ""
        try:
            output = check_output(cmd).decode('utf_8')
        except Exception as e:
            log.loge(e)

        output = output.replace("Off", "On")

        for dev in output.splitlines():
            command = ['indi_setprop', dev]
            log.logd(command)
            run(command)

    def get_running_drivers(self) -> list:
        """
            Get the list of running drivers
            Args : None
            Returns : list
        """
        drivers = self.__running_drivers
        return drivers