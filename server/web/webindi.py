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

import os,json
from threading import Timer
from flask import render_template,make_response,request,Flask
from flask_login import login_required

from server.indi.indiserver import IndiServer
from server.indi.indidriver import DriverCollection
from server.indi.indidatabase import Database
from server.indi.indidevice import Device

import server.config as c

collection = DriverCollection(c.config["indiweb"]["data"])
indi_server = IndiServer(c.config["indiweb"]["fifo"])
indi_device = Device()
db_path = os.path.join("config", 'indiweb','profiles.db')
db = Database(db_path)
collection.parse_custom_drivers(db.get_custom_drivers())

saved_profile = None
active_profile = ""

from utils.lightlog import lightlog
log = lightlog(__name__)

def start_profile(profile):
    info = db.get_profile(profile)

    profile_drivers = db.get_profile_drivers_labels(profile)
    all_drivers = [collection.by_label(d['label']) for d in profile_drivers]
    indi_server.start(info['port'], all_drivers)
        # Auto connect drivers in 3 seconds if required.
    if info['autoconnect'] == 1:
        t = Timer(3, indi_server.auto_connect)
        t.start()
        
def create_indiweb_manager(app : Flask,csrf) -> None:
    """
        Creates an IndiWebManager instance.
        Args : 
            app: The Flask application instance.
            csfr : The CSRF context protection
        Returns :
            None
    """
    @app.route('/indiweb',methods=['GET'])
    @app.route("/indiweb/",methods=['GET'])
    @app.route("/indiweb.html",methods=['GET'])
    @login_required
    def indiweb():
        """Main page"""
        global saved_profile
        drivers = collection.get_families()

        if not saved_profile:
            saved_profile = request.cookies.get('indiserver_profile') or 'Simulators'
        
        profiles = db.get_profiles()
        return render_template('indiweb.html', profiles=profiles,
                        drivers=drivers, saved_profile=saved_profile)

    ###############################################################################
    # Profile endpoints
    ###############################################################################

    @app.route('/indiweb/api/profiles', methods=['GET'])
    @app.route('/indiweb/api/profiles/', methods=['GET'])
    @login_required
    def get_json_profiles():
        """Get all profiles (JSON)"""
        results = db.get_profiles()
        return json.dumps(results)
    
    @app.route('/indiweb/api/profiles/<item>', methods=['GET'])
    @app.route('/indiweb/api/profiles/<item>/', methods=['GET'])
    @login_required
    def get_json_profile(item):
        """Get one profile info"""
        results = db.get_profile(item)
        return json.dumps(results)

    @app.route('/indiweb/api/profiles/<name>', methods=['POST'])
    @app.route('/indiweb/api/profiles/<name>/', methods=['POST'])
    @login_required
    @csrf.exempt
    def add_profile(name):
        """Add new profile"""
        db.add_profile(name)
        return ''

    @app.route('/indiweb/api/profiles/<name>', methods=['DELETE'])
    @app.route('/indiweb/api/profiles/<name>/', methods=['DELETE'])
    @login_required
    @csrf.exempt
    def delete_profile(name):
        """Delete Profile"""
        db.delete_profile(name)
        return ''

    @app.route('/indiweb/api/profiles/<name>', methods=['PUT'])
    @app.route('/indiweb/api/profiles/<name>/', methods=['PUT'])
    @login_required
    @csrf.exempt
    def update_profile(name):
        """Update profile info (port & autostart & autoconnect)"""
        resp = make_response("set cookie")
        resp.set_cookie("indiserver_profile", name, path='/')
        data = request.json
        port = data.get('port', c.config["indiweb"][""])
        autostart = bool(data.get('autostart', 0))
        autoconnect = bool(data.get('autoconnect', 0))
        db.update_profile(name, port, autostart, autoconnect)
        return ''

    @app.route('/indiweb/api/profiles/<name>/drivers', methods=['POST'])
    @app.route('/indiweb/api/profiles/<name>/drivers/', methods=['POST'])
    @login_required
    @csrf.exempt
    def save_profile_drivers(name):
        """Add drivers to existing profile"""
        data = request.json
        db.save_profile_drivers(name, data)
        return ''


    @app.route('/indiweb/api/profiles/custom', methods=['POST'])
    @app.route('/indiweb/api/profiles/custom/', methods=['POST'])
    @login_required
    @csrf.exempt
    def save_profile_custom_driver():
        """Add custom driver to existing profile"""
        data = request.json(silent=False)
        db.save_profile_custom_driver(data)
        collection.clear_custom_drivers()
        collection.parse_custom_drivers(db.get_custom_drivers())


    @app.route('/indiweb/api/profiles/<item>/labels', methods=['GET'])
    @app.route('/indiweb/api/profiles/<item>/labels/', methods=['GET'])
    @login_required
    def get_json_profile_labels(item):
        """Get driver labels of specific profile"""
        results = db.get_profile_drivers_labels(item)
        return json.dumps(results)

    @app.route('/indiweb/api/profiles/<item>/remote', methods=['GET'])
    @app.route('/indiweb/api/profiles/<item>/remote/', methods=['GET'])
    @login_required
    def get_remote_drivers(item):
        """Get remote drivers of specific profile"""
        results = db.get_profile_remote_drivers(item)
        if results is None:
            results = {}
        return json.dumps(results)


    ###############################################################################
    # Server endpoints
    ###############################################################################

    @app.route('/indiweb/api/server/status', methods=['GET'])
    @app.route('/indiweb/api/server/status/', methods=['GET'])
    @login_required
    def get_server_status():
        """
            Get server status information | 获取服务器状态
            Args : None
            Returns : None
        """
        status = [{'status': str(indi_server.is_running()), 'active_profile': active_profile}]
        return json.dumps(status)


    @app.route('/indiweb/api/server/drivers', methods=['GET'])
    @app.route('/indiweb/api/server/drivers/', methods=['GET'])
    @login_required
    def get_server_drivers():
        """
            List all of the driver | 列出所有设备
            Args : None
            Returns : json
        """
        drivers = []
        if indi_server.is_running() is True:
            for driver in indi_server.get_running_drivers().values():
                drivers.append(driver.__dict__)
        return json.dumps(drivers)


    @app.route('/indiweb/api/server/start/<profile>', methods=['POST'])
    @app.route('/indiweb/api/server/start/<profile>/', methods=['POST'])
    @login_required
    @csrf.exempt
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


    @app.route('/indiweb/api/server/stop', methods=['POST'])
    @app.route('/indiweb/api/server/stop/', methods=['POST'])
    @login_required
    @csrf.exempt
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

    @app.route('/indiweb/api/drivers/groups', methods=['GET'])
    @app.route('/indiweb/api/drivers/groups/', methods=['GET'])
    @login_required
    def get_json_groups():
        """Get all driver families (JSON)"""
        families = collection.get_families()
        return json.dumps(sorted(families.keys()))


    @app.route('/indiweb/api/drivers', methods=['GET'])
    @app.route('/indiweb/api/drivers/', methods=['GET'])
    @login_required
    def get_json_drivers():
        """Get all drivers (JSON)"""
        return json.dumps([ob.__dict__ for ob in collection.drivers])


    @app.route('/indiweb/api/drivers/start/<label>', methods=['POST'])
    @app.route('/indiweb/api/drivers/start/<label>/', methods=['POST'])
    @login_required
    def start_driver(label):
        """Start INDI driver"""
        driver = collection.by_label(label)
        indi_server.start_driver(driver)
        log.log('Driver "%s" started.' % label)
        return ''

    @app.route('/indiweb/api/drivers/stop/<label>', methods=['POST'])
    @app.route('/indiweb/api/drivers/stop/<label>/', methods=['POST'])
    @login_required
    @csrf.exempt
    def stop_driver(label):
        """Stop INDI driver"""
        driver = collection.by_label(label)
        indi_server.stop_driver(driver)
        log.log('Driver "%s" stopped.' % label)
        return ''


    @app.route('/indiweb/api/drivers/restart/<label>', methods=['POST'])
    @app.route('/indiweb/api/drivers/restart/<label>/', methods=['POST'])
    @login_required
    @csrf.exempt
    def restart_driver(label):
        """Restart INDI driver"""
        driver = collection.by_label(label)
        indi_server.stop_driver(driver)
        indi_server.start_driver(driver)
        log.log('Driver "%s" restarted.' % label)
        return ''

    ###############################################################################
    # Device endpoints
    ###############################################################################


    @app.route('/indiweb/api/devices', methods=['GET'])
    @app.route('/indiweb/api/devices/', methods=['GET'])
    @login_required
    def get_devices():
        return json.dumps(indi_device.get_devices())

    ###############################################################################
    # Startup standalone server
    ###############################################################################


    def main():
        """Start autostart profile if any"""
        global active_profile

        for profile in db.get_profiles():
            if profile['autostart']:
                start_profile(profile['name'])
                active_profile = profile['name']
                break

        log.log("Exiting")
