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

import os,json,socket,subprocess
from threading import Timer

from flask import Flask, request, render_template, make_response

from server.indiweb.indi_server import INDIServerFIFO
from server.indiweb.indi_driver import INDIDriverCollection
from server.indiweb.indi_database import Database
from server.indiweb.indi_device import Device

from utils.lightlog import lightlog
log = lightlog(__name__)

from utils.i18n import _
# default settings
WEB_HOST = '0.0.0.0'
WEB_PORT = 8624

indiapp = Flask(__name__,
    static_folder = os.path.join(os.getcwd(),"client","static"),
    template_folder= os.path.join(os.getcwd(),"client","templates"),
)

indi_collection = None
indi_server = None
indi_device = None
indi_database = None
saved_profile = None
active_profile = ""

@indiapp.route("/")
def index():
    global saved_profile
    drivers = indi_collection.get_families()
    if not saved_profile:
        saved_profile = request.cookies.get('indiserver_profile') or 'Simulators'
    profiles = indi_database.get_profiles()
    hostname = socket.gethostname()
    return render_template('indiweb.html',profiles=profiles,
                    drivers=drivers, saved_profile=saved_profile,
                    hostname=hostname)

@indiapp.route('/api/profiles', methods=['GET'])
def get_json_profiles():
    """Get all profiles (JSON)"""
    results = indi_database.get_profiles()
    return json.dumps(results)
   
@indiapp.route('/api/profiles/<item>', methods=['GET'])
def get_json_profile(item):
    """Get one profile info"""
    results = indi_database.get_profile(item)
    return json.dumps(results)

@indiapp.route('/api/profiles/<name>', methods=['POST'])
def add_profile(name):
    """Add new profile"""
    indi_database.add_profile(name)
    return ''

@indiapp.route('/api/profiles/<name>', methods=['DELETE'])
def delete_profile(name):
    """Delete Profile"""
    indi_database.delete_profile(name)
    return ''

@indiapp.route('/api/profiles/<name>', methods=['PUT'])
def update_profile(name):
    """Update profile info (port & autostart & autoconnect)"""
    resp = make_response("set cookie")
    resp.set_cookie("indiserver_profile", name, path='/')
    data = request.json
    port = data.get('port', 7624)
    autostart = bool(data.get('autostart', 0))
    autoconnect = bool(data.get('autoconnect', 0))
    indi_database.update_profile(name, port, autostart, autoconnect)
    return ''

@indiapp.route('/api/profiles/<name>/drivers', methods=['POST'])
def save_profile_drivers(name):
    """Add drivers to existing profile"""
    data = request.json
    indi_database.save_profile_drivers(name, data)
    return ''


@indiapp.route('/api/profiles/custom', methods=['POST'])
def save_profile_custom_driver():
    """Add custom driver to existing profile"""
    data = request.json(silent=False)
    indi_database.save_profile_custom_driver(data)
    indi_collection.clear_custom_drivers()
    indi_collection.parse_custom_drivers(indi_database.get_custom_drivers())


@indiapp.route('/api/profiles/<item>/labels', methods=['GET'])
def get_json_profile_labels(item):
    """Get driver labels of specific profile"""
    results = indi_database.get_profile_drivers_labels(item)
    return json.dumps(results)


@indiapp.route('/api/profiles/<item>/remote', methods=['GET'])
def get_remote_drivers(item):
    """Get remote drivers of specific profile"""
    results = indi_database.get_profile_remote_drivers(item)
    if results is None:
        results = {}
    return json.dumps(results)


###############################################################################
# Server endpoints
###############################################################################

@indiapp.route('/api/server/status', methods=['GET'])
def get_server_status():
    """Server status"""
    status = [{'status': str(indi_server.is_running()), 'active_profile': active_profile}]
    return json.dumps(status)


@indiapp.route('/api/server/drivers', methods=['GET'])
def get_server_drivers():
    """List server drivers"""
    # status = []
    # for driver in indi_server.get_running_drivers():
    #     status.append({'driver': driver})
    # return json.dumps(status)
    # labels = []
    # for label in sorted(indi_server.get_running_drivers().keys()):
    #     labels.append({'driver': label})
    # return json.dumps(labels)
    drivers = []
    if indi_server.is_running() is True:
        for driver in indi_server.get_running_drivers().values():
            drivers.append(driver.__dict__)
    return json.dumps(drivers)


@indiapp.route('/api/server/start/<profile>', methods=['POST'])
def start_server(profile):
    """Start INDI server for a specific profile"""
    global saved_profile
    saved_profile = profile
    global active_profile
    active_profile = profile
    res = make_response()
    res.set_cookie("indiserver_profile", profile)
    start_profile(profile)
    return ''


@indiapp.route('/api/server/stop', methods=['POST'])
def stop_server():
    """Stop INDI Server"""
    indi_server.stop()

    global active_profile
    active_profile = ""

    # If there is saved_profile already let's try to reset it
    global saved_profile
    if saved_profile:
        saved_profile = request.cookies.get("indiserver_profile") or "Simulators"
    return ''


###############################################################################
# Driver endpoints
###############################################################################

@indiapp.route('/api/drivers/groups', methods=['GET'])
def get_json_groups(response):
    """Get all driver families (JSON)"""
    response.content_type = 'application/json'
    families = indi_collection.get_families()
    return json.dumps(sorted(families.keys()))


@indiapp.route('/api/drivers', methods=['GET'])
def get_json_drivers(response):
    """Get all drivers (JSON)"""
    response.content_type = 'application/json'
    return json.dumps([ob.__dict__ for ob in indi_collection.drivers])


@indiapp.route('/api/drivers/start/<label>', methods=['POST'])
def start_driver(label):
    """Start INDI driver"""
    driver = indi_collection.by_label(label)
    indi_server.start_driver(driver)
    log.log(_('Driver "%s" started.') % label)
    return ''



@indiapp.route('/api/drivers/stop/<label>', methods=['POST'])
def stop_driver(label):
    """Stop INDI driver"""
    driver = indi_collection.by_label(label)
    indi_server.stop_driver(driver)
    log.log(_('Driver "%s" stopped.') % label)
    return ''


@indiapp.route('/api/drivers/restart/<label>', methods=['POST'])
def restart_driver(label):
    """Restart INDI driver"""
    driver = indi_collection.by_label(label)
    indi_server.stop_driver(driver)
    indi_server.start_driver(driver)
    log.log(_('Driver "%s" restarted.') % label)
    return ''

###############################################################################
# Device endpoints
###############################################################################


@indiapp.route('/api/devices', methods=['GET'])
def get_devices():
    return json.dumps(indi_device.get_devices())

###############################################################################
# System control endpoints
###############################################################################


@indiapp.route('/api/system/reboot', methods=['POST'])
def system_reboot():
    """reboot the system running indi-web"""
    log.log(_('System reboot, stopping server...'))
    stop_server()
    log.log(_('rebooting...'))
    subprocess.run('reboot')

@indiapp.route('/api/system/poweroff', methods=['POST'])
def system_poweroff():
    """poweroff the system"""
    log.log(_('System poweroff, stopping server...'))
    stop_server()
    log.log(_('poweroff...'))
    subprocess.run("poweroff")

def start_profile(profile):
    info = indi_database.get_profile(profile)

    profile_drivers = indi_database.get_profile_drivers_labels(profile)
    all_drivers = [indi_collection.by_label(d['label']) for d in profile_drivers]
    indi_server.start(info['port'], all_drivers)
        # Auto connect drivers in 3 seconds if required.
    if info['autoconnect'] == 1:
        t = Timer(3, indi_server.auto_connect)
        t.start()

def start_indiweb(host : str, port : int,indi_port : int,fifo_path : str,config_path : str,data_path : str):
    """
        Start INDI web manager
        Args:
            host : str # host of the INDI web manager
            port : int # port of the INDI web manager
            indi_port : int # port of the INDI server
            fifo_path : str # path of the INDI fifo
            config_path : str # path of the INDI config
            data_path : str # path of the INDI data (xml files)
    """
    _host = host if host is not None else "0.0.0.0"
    _port = port if port is not None else 8624
    _indi_port = indi_port if indi_port is not None else 7624
    _fifo_path = fifo_path if fifo_path is not None else "/tmp/indiFIFO"
    _config_path = config_path if config_path is not None else "/tmp/indi"
    _data_path = data_path if data_path is not None else "/usr/share/indi"
    global indi_collection
    global indi_server
    global indi_device
    global indi_database
    indi_collection = INDIDriverCollection(_data_path)
    indi_server = INDIServerFIFO(_fifo_path, _config_path)
    indi_device = Device(port=_indi_port)
    indi_database = Database(os.path.join(os.getcwd(),"config","indiweb","profiles.db"))
    indi_collection.parse_custom_drivers(indi_database.get_custom_drivers())
    indiapp.jinja_env.auto_reload = True
    global active_profile
    for profile in indi_database.get_profiles():
        if profile['autostart']:
            start_profile(profile['name'])
            active_profile = profile['name']
            break

    log.log(_("Exiting"))
    indiapp.run(host=_host, port=_port, debug=True, threaded=True)


if __name__ == '__main__':
    start_indiweb()
