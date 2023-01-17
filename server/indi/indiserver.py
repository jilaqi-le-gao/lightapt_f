#!/usr/bin/python

from subprocess import getoutput, call, check_output

import server.config as c

from utils.lightlog import lightlog
log = lightlog(__name__)

class IndiServer(object):
    def __init__(self, fifo = c.config["indiweb"]["fifo"]):
        self.__fifo = fifo
        self.__running_drivers = {}        

    def start(self, port = c.config["indiweb"]["port"], drivers = []) -> None:
        """
            Start INDI server by command line
            Args : 
                port : int # the port of the INDI server
                drivers : list of str # name of the drivers in INDI data(xml)
            Returns : None
        """
        # If there is a INDI server running , just kill it
        if self.is_running():
            self.stop()
        # Clear the old fifo pipe and create a new one
        log.log("Deleting fifo %s" % self.__fifo)
        call(['rm', '-f', self.__fifo])
        call(['mkfifo', self.__fifo])
        # Just start the server without driver
        cmd = 'indiserver -p %d -m 100 -v -f %s > /tmp/indiserver.log 2>&1 &' % (port, self.__fifo)
        log.log(cmd)
        call(cmd, shell=True)

        self.__running_drivers = {}
        # Start driver one by one
        for driver in drivers:
            self.start_driver(driver)

    def stop(self) -> None:
        """
            Stop INDI server by command line
            Args : None
            Returns : None
        """
        cmd = "killall indiserver >/dev/null 2>&1"
        ret = call(cmd, shell=True)
        if ret == 0:
            log.log('indiserver terminated successfully')

    def is_running(self):
        if getoutput("ps -ef | grep indiserver | grep -v grep | wc -l") != "0":
            return True
        return False

    def start_driver(self, driver : dict) -> None:
        """
            Start a driver and send the command to the server via FIFO connection
            Args : 
                driver : dict # dict containing INDI driver information
            Returns : None
        """
        cmd = 'start %s' % driver.binary

        if driver.skeleton:
            cmd += ' -s "%s"' % driver.skeleton

        cmd = cmd.replace('"', '\\"')
        full_cmd = 'echo "%s" > %s' % (cmd, self.__fifo)
        log.log(full_cmd)
        call(full_cmd, shell=True)
        self.__running_drivers[driver.label] = driver

    def stop_driver(self, driver : str) -> None:
        """
            Stop a driver and send the command to the server via FIFO connection
            Args : 
                driver : str # name of the driver in INDI data(xml)
            Returns : None
        """
        cmd = 'stop %s' % driver.binary

        if "@" not in driver.binary:
            cmd += ' -n "%s"' % driver.label
        cmd = cmd.replace('"', '\\"')
        full_cmd = 'echo "%s" > %s' % (cmd, self.__fifo)
        log.log(full_cmd)
        call(full_cmd, shell=True)
        del self.__running_drivers[driver.label]

    def set_prop(self, dev : str, prop : str, element : str, value : str) -> None:
        """
            Set a property of a device
            Args : 
                dev : str # name of the device
                prop : str # name of the property
                element : str # name of the element
                value : str # value of the property
            Returns : None
        """
        cmd = ['indi_setprop', '%s.%s.%s=%s' % (dev, prop, element, value)]
        call(cmd)

    def get_prop(self, dev : str, prop : str, element : str) -> bytes:
        """
            Get a property of a device
            Args : 
                dev : str # name of the device
                prop : str # name of the property
                element : str # name of the element
            Returns : bytes
        """
        cmd = ['indi_getprop', '%s.%s.%s' % (dev, prop, element)]
        output = check_output(cmd)
        return output.split('=')[1].strip()

    def get_state(self, dev : str, prop : str) -> bytes:
        """
            Get a property of a device
            Args : 
                dev : str # name of the device
                prop : str # name of the property
            Returns : bytes
        """
        return self.get_prop(dev, prop, '_STATE')

    def auto_connect(self) -> None:
        """
            Auto connect to the device when starting the server
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
            log.log(command)
            call(command)

    def get_running_drivers(self) -> dict:
        """
            Get all running drivers
            Args : None
            Returns : dict
        """
        drivers = self.__running_drivers
        return drivers
