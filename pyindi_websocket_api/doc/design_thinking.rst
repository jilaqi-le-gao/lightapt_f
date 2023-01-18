data_struct
==================

use tornado to start websocket, to show basic details and do operations to all devices.

websocket define
============================

websocket debug
----------------------

url: /ws/debugging/

role:

* show device all status, including data values
* show specific device data status, example, input telescope, show all telescope data.
* show specific data value, input telescope coord, show telescope coord only
* advanced, using single command, or json, change status. this probably is not necessary. will be developed later.

websocket control
-----------------------

url: /ws/indi_client/

role:

* do direct control to all device, currently include: CCD, telescope. Only one CCD and telescope is supported.
* periodically send system brief status.

http define
==================

http indi device add remove
-----------------------------------

url: /device_FIFO/
method: post

role:

* get info from other control panels, to manage the indi_incoming_device_info, ensure each device has only one.
* this will only remember the newest incoming device. e.g. if there were one CCD simulator connected. then if FIFO
    has bumped up another new brand CCD. then this user interface will only remember and use hte new brand CCD.


control command design
============================

telescope
------------

connect_device

disconnect_device

goto(ra, dec)

goto_thread(ra, dec)  Continue getting goto status and return to client

abort_goto()

park()

unpark()

home()

set_park_position()

track()

stop_track()

set_track_rate()

set_track_mode()

get_location()  ? really need?

goto_by_relative()

CCD
--------

connect_device

disconnect_device

TBD

class structure
=======================

PyIndiWebSocket contains:

    indiclient                  pyindi_client instance
    indi_device_info            saves all device information
    telescope_device            all device actions, contains pyindi BaseDevice for telescope, inherited from IndiBaseDevice
    camera_device               all device actions, contains pyindi BaseDevice for camera, inherited from IndiBaseDevice

