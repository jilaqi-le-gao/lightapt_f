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

# #################################################################
# This file contains all of the html pages needed to create
# #################################################################

import requests
from flask import render_template,redirect,request,url_for
from flask_login import login_required

def create_html_page(app) -> None:
    """
        Create html pages 
        Args : 
            app : Flask application object
        Returns :
            None
    """

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/camera',methods=['GET'])
    @login_required
    def camera():
        return render_template('camera.html')

    @app.route('/camera/',methods=['GET'])
    @login_required
    def camera_():
        return redirect("/camera")

    @app.route('/camera.html',methods=['GET'])
    @login_required
    def camera_html():
        return redirect('/camera')
        
    @app.route('/telescope',methods=['GET'])
    @login_required
    def telescope():
        return render_template('telescope.html')

    @app.route('/telescope/',methods=['GET'])
    @login_required
    def telescope_():
        return redirect("/telescope")

    @app.route('/telescope.html',methods=['GET'])
    @login_required
    def telescope_html():
        return redirect('/telescope')

    @app.route('/focuser',methods=['GET'])
    @login_required
    def focuser():
        return render_template('focuser.html')

    @app.route('/focuser/',methods=['GET'])
    @login_required
    def focuser_():
        return redirect("/focuser")

    @app.route('/focuser.html',methods=['GET'])
    @login_required
    def focuser_html():
        return redirect('/focuser')

    @app.route('/guider',methods=['GET'])
    @login_required
    def guider():
        return render_template('guider.html')

    @app.route('/guider/',methods=['GET'])
    @login_required
    def guider_():
        return redirect("/guider")

    @app.route('/guider.html',methods=['GET'])
    @login_required
    def guider_html():
        return redirect('/guider')

    @app.route('/solver',methods=['GET'])
    @login_required
    def solver():
        return render_template('solver.html')

    @app.route('/solver/',methods=['GET'])
    @login_required
    def solver_():
        return redirect("/solver")

    @app.route('/solver.html',methods=['GET'])
    @login_required
    def solver_html():
        return redirect('/solver')
        
    @app.route('/novnc',methods=['GET'])
    @login_required
    def novnc():
        return render_template('novnc.html')

    @app.route('/novnc/',methods=['GET'])
    @login_required
    def novnc_():
        return redirect("/novnc")

    @app.route('/novnc.html',methods=['GET'])
    @login_required
    def novnc_html():
        return redirect('/novnc')

    @app.route('/client',methods=['GET'])
    @login_required
    def client():
        return render_template('client.html')

    @app.route('/client/',methods=['GET'])
    @login_required
    def client_():
        return redirect("/client")

    @app.route('/client.html',methods=['GET'])
    @login_required
    def client_html():
        return redirect('/client')

    @app.route('/desktop',methods=['GET'])
    @login_required
    def desktop():
        return render_template('desktop.html')

    @app.route('/desktop/',methods=['GET'])
    @login_required
    def desktop_():
        return redirect("/desktop")

    @app.route('/desktop.html',methods=['GET'])
    @login_required
    def desktop_html():
        return redirect('/desktop')

    @app.route("/ndesktop",methods=['GET'])
    @login_required
    def ndesktop():
        return render_template('ndesktop.html')

    @app.route("/ndesktop/",methods=['GET'])
    @login_required
    def ndesktop_():
        return redirect("/ndesktop")

    @app.route("/ndesktop.html",methods=['GET'])
    @login_required
    def ndesktop_html():
        return redirect("/ndesktop")

    @app.route("/skymap",methods=['GET'])
    @login_required
    def skymap():
        return render_template('skymap.html')

    @app.route("/skymap/",methods=['GET'])
    @login_required
    def skymap_():
        return redirect("/skymap")

    @app.route("/skymap.html",methods=['GET'])
    @login_required
    def skymap_html():
        return redirect("/skymap")

    @app.route("/scripteditor",methods=['GET'])
    @login_required
    def scripteditor():
        return render_template('scripteditor.html')

    @app.route("/scripteditor/",methods=['GET'])
    @login_required
    def scripteditor_():
        return redirect("/scripteditor")

    @app.route("/scripteditor.html",methods=['GET'])
    @login_required
    def scripteditor_html():
        return redirect("/scripteditor")

    @app.route("/imageviewer",methods=['GET'])
    @login_required
    def imageviewer():
        return render_template('imageviewer.html')

    @app.route("/imageviewer/",methods=['GET'])
    @login_required
    def imageviewer_():
        return redirect("/imageviewer")

    @app.route("/imageviewer.html",methods=['GET'])
    @login_required
    def imageviewer_html():
        return redirect("/imageviewer")

    @app.route("/webssh" , methods=['GET'])
    @login_required
    def webssh():
        return redirect("http://127.0.0.1:8888",code=301)

    @app.route("/webssh/", methods=['GET'])
    @login_required
    def webssh_():
        return redirect("/webssh")

    @app.route("/webssh.html", methods=['GET'])
    @login_required
    def webssh_html():
        return redirect("/webssh")

    @app.route("/tools" , methods=['GET'])
    @login_required
    def tools():
        return render_template("tools.html")

    @app.route("/tools/", methods=['GET'])
    @login_required
    def tools_():
        return redirect("/tools")
    
    @app.route("/tools.html", methods=['GET'])
    @login_required
    def tools_html():
        return redirect("/tools")
        
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template('500.html'), 500
