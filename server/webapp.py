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

import os,json,logging,uuid

from utils.i18n import _
import server.config as c

from flask import Flask,render_template,redirect,Blueprint,request
from flask_login import LoginManager,login_required,login_user,logout_user,UserMixin
from werkzeug.security import check_password_hash,generate_password_hash

app = Flask(__name__,
    static_folder=os.path.join(os.getcwd(),"client","static"),
    template_folder=os.path.join(os.getcwd(),"client","templates")
)
app.secret_key = "lightapt"
auth = Blueprint("auth",__name__)
# Login system
login_system = LoginManager()
login_system.session_protection = "strong"
login_system.login_view = "login"
login_system.login_message_category = "info"
login_system.login_message = "Access denied."
login_system.init_app(app)

USERS = [
    {"id" : 1 ,"username": "admin", "password": generate_password_hash("admin")},
]

def create_user(user_name : str, password : str) -> None:
    """
        Create a new user | 创建一个新的用户
        Args:
            user_name: str
            password: str
    """
    user = {
        "name": user_name,
        "password": generate_password_hash(password),
        "id": uuid.uuid4()
    }
    USERS.append(user)

def get_user(user_name : str) -> UserMixin:
    """
        Get the user from the database
        Args:
            user_name: str
        Returns:
            UserMixin | None if the user is not available
    """
    for user in USERS:
        if user.get("username") == user_name:
            return user
    return None

@login_system.user_loader
def load_user(user_id : str):
    """
        Get the user from the database
        Args:
            user_id: str
        Returns:
            UserMixin | None if the user is not available
    """
    return User.get(user_id)

class User(UserMixin):
    """
        User Information object
    """
    def __init__(self, user):
        self.username = user.get("name")
        self.password_hash = user.get("password")
        self.id = user.get("id")

    def verify_password(self, password):
        """密码验证"""
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """获取用户ID"""
        return self.id

    @staticmethod
    def get(user_id):
        if not user_id:
            return None
        for user in USERS:
            if user.get('id') == user_id:
                return User(user)
        return None

@app.route("/login" , methods=["POST","GET"])
def login():
    """
        Login
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_info = get_user(username)
        if username is None or password is None:
            log.loge(_("Empty username or password"))
            return redirect("/login")
        if user_info is None:
            return redirect("/login")
        else:
            user = User(user_info)
            if user.verify_password(password):  # 校验密码
                login_user(user)
                log.log(_("User login successful"))
                return redirect('/desktop')
    return render_template('login.html')

@app.route("/login/" , methods=["POST","GET"])
def login_():
    return redirect('/login')

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    log.logd(_("User has been logged out"))
    return redirect('/')

@app.route("/logout/" , methods=["GET"])
@login_required
def logout_():
    return redirect('/logout')

# Disable Flask logging system
if not c.config.get('debug'):
    logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.ERROR)
logger = logging.getLogger('waitress')
logger.setLevel(logging.ERROR)

import server.config as c

from server.webpage import create_html_page
create_html_page(app)
from server.webindi import create_indiweb_manager
create_indiweb_manager(app)
from server.websys import create_web_sysinfo
create_web_sysinfo(app)

def run_server() -> None:
    """
        Start the server | 启动服务器
        Args: None
        Return: None
        NOTE : All of the c.configuration parameters are already defined before starting the server
    """
    if c.config.get("debug") is True:
        log.log(_("Running debug web server on {}:{}").format(c.config.get('host'),c.config.get('port')))
        app.run(host=c.config.get("host"), port=c.config.get("port"),threaded=c.config.get("threaded"),debug=c.config.get("debug"))
    else:
        log.log(_("Running web server on {}:{}").format(c.config.get('host'),c.config.get('port')))
        try:
            # We hope to use waitress as a high performance wsgi server
            from waitress import serve
            log.log(_("Using waitress as wsgi server"))
            serve(app,host = c.config.get("host"),port=c.config.get("port"))
        except ImportError as e:
            logger.logw(_("Failed to import waitress as wsgi server , use default server"))
            app.run(host=c.config.get("host"),port=c.config.get("port"),threaded=True)
        