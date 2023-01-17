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

from flask_login import login_required
from flask import Flask,render_template
from utils.i18n import _
from utils.utility import Download

import server.config as c
import server.basic.astrometry as ast

def create_web_tools(app : Flask):
    """
        Create a web application tools
    """

    @app.route("/tools/api/time/<time>",methods=["GET"])
    @login_required
    def api_time(time : str):
        """
            Time settings API method
            Args : 
                time : str
            Returns : None
        """
        print(time)
        return {"message" : _("Set time successfully")}

    @app.route("/tools/api/location/<float:lon>/<float:lat>",methods=["GET"])
    @app.route("/tools/api/location/<float:lon>/<float:lat>/",methods=["GET"])
    @login_required
    def api_location(lon : float,lat : float):
        """
            Location settings API method
            Args : 
                lon : float # the latitude of the location
                lat : float # the longitude of the location
            Returns : None
        """
        print(lat,lon)
        if not 0 <= lat <= 90:
            return {"error": _("Invalid latitude")}
        if not 0 <= lon <= 180:
            return {"error": _("Invalid longitude")}
        c.config["location"] = {
            "latitude" : lat,
            "longitude" : lon
        }
        return {"message": _("Set location successfully")}

    @app.route("/tools/api/download/astap/<file>",methods=["GET"])
    @app.route("/tools/api/download/astap/<file>/",methods=["GET"])
    @login_required
    def api_download_astap():
        """
            Download ASTAP solving templates files from Internet
            Args : None
            Returns : None
        """

    @app.route("/tools/api/download/astrometry/<file>",methods=["GET"])
    @app.route("/tools/api/download/astrometry/<file>/",methods=["GET"])
    @login_required
    def api_download_astrometry():
        """
            Download Astrometry solving templates files from Internet
            Args : None
            Returns : None
        """

    @app.route("/tools/api/download/astap/already",methods=["GET"])
    @app.route("/tools/api/download/astap/already/",methods=["GET"])
    @login_required
    def api_download_astap_already():
        """
            Chheck if the ASTAP templates had been downloaded
            Args : None
            Returns : None
        """

    @app.route("/tools/api/download/astrometry/already",methods=["GET"])
    @app.route("/tools/api/download/astrometry/already/",methods=["GET"])
    @login_required
    def api_download_astrometry_already():
        """
            Check if the astrometry solving templates had been downloaded
            Args : None
            Returns : None
        """