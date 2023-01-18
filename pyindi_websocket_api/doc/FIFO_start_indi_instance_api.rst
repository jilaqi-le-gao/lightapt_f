FIFO start up device api
===========================

default as using FIFO to start up all device to indi, then the start information need to be
transmit to this websocket interface to get indi BaseDevice.

This is done by calling api

start up procedure
----------------------------

first time start up
++++++++++++++++++++++++++++

if the system is start up first time, it need configuration driver type and setup device usage.

procedure is:

1. select driver type(or name), start indi
2. use `get all devices` api, get all indi connected driver devices, include name, driver type, device name.
3. wait user to configure which device is used as what purpose.
4. send the device configuration by `start device` api.
5. only when start device api is called, device will be connected. The device configuration should be saved
somewhere.

one-shot start up
++++++++++++++++++++++++++

once the device configuration is saved, then one-shot start up can be carried out.

1. select device configuration.
2. start indi, with respect to selected device drivers.
3. direct send the device name through `start device` api.
4. everything will be set.

api definition
==================

get all devices
------------------

localhost:7999/get/all/devices/

through this url, you will get a json response, which contains::

    [
        {
            'device_name': str, which is the device name should be saved and directly send through `start device` api
            'device_driver_name': str, name of device driver,
            'device_driver_exec': str, the exec name of device driver, which is send by FIFO or when indi is started.
            'driver_version': str, in case if it is needed
        },
        {} ...
    ]

start device
------------------

when a device is started by FIFO, this url should be called immediately:

    localhost:7999/FIFO/start/device_type/device_name/

when a device is closed by FIFO, this url should be called:

    localhost:7999/FIFO/stop/device_type/device_name/


e.g.

    if CCD simulator is configured as camera, then send localhost:7999/FIFO/start/camera/CCD Simulator/


current supported device type will be::

    telescope
    camera
    focuser
    filter_wheel
