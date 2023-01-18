telescope data struct and instruction definition
=========================================================

private data saved by websocket interface
-------------------------------------------------

* longitude
* latitude
* elevation

* max_alt             limitation for alt
* min_alt

initial after connection
+++++++++++++++++++++++++++++

* can_set_max_alt   
* can_park
* can_home
* can_track_speed
* can_slew_speed
* can_guide_speed

minimum instruction set
----------------------------

* set_long_lat
* get_static_info       get telescope static information which cannot be changed
* get_set_params        get important setting params
* get_all_params
* set_param
* get_real_time_info    get ra dec ha dec alt az
* goto                  goto ra dec
* goto_ha_dec
* goto_alt_az
* set_track_rate
* start_track
* stop_track
* park
* unpark
* set_park
* home
* at_home
* set_track_speed
* set_slew_speed
* set_guiding_speed
* move_direction

telescope api definition
==========================

set_long_lat
-------------

instruction name:    set_long_lat

used as:  define the GEOGRAPHIC_COORD information

params: [longitude, latitude, elevation(optional, default as 0)]

return: None

get_static_info
--------------------------------


get_set_params
-----------------------------------

