# coding=utf-8

"""

Copyright(c) 2022-2023 Max Qian  <astroair.cn>

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
from flask_wtf import CSRFProtect,FlaskForm
from werkzeug.security import check_password_hash,generate_password_hash
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__,
    static_folder=os.path.join(os.getcwd(),"client","static"),
    template_folder=os.path.join(os.getcwd(),"client","templates")
)
app.secret_key = "lightapt"
# Add form fields protection
csrf = CSRFProtect(app)

auth = Blueprint("auth",__name__)
# Login system
login_system = LoginManager()
login_system.session_protection = "strong"
login_system.login_view = "login"
login_system.login_message_category = "info"
login_system.login_message = "Access denied."
login_system.init_app(app)

USERS = None

def load_password() -> None:
    """
        Load the password from the json file
        Args : None
        Returns : None
    """
    _path = os.path.join(os.getcwd(),"config","password.json")
    if not os.path.exists(_path):
        log.loge(_("Could not find password.json , try to create a new one with default password"))
        if not os.path.exists(os.path.join(os.getcwd(),"config")):
            os.mkdir(os.path.join(os.getcwd(),"config"))
        try:
            with open(_path,mode="w+",encoding="utf-8") as f:
                f.write(json.dump([
                    {"id" : 1 ,"username": "admin", "password": generate_password_hash("admin")},
                ]))
        except OSError as e:
            log.loge(_("Failed to create password file : {}").format(str(e)))
            return
    try:
        with open(_path,mode="r" , encoding="utf-8") as f:
            global USERS
            USERS = json.loads(f.read())
    except OSError as e:
        log.loge(_("Failed to load password from json file : {}").format(str(e)))
    except json.JSONDecodeError as e:
        log.loge(_("Failed to decode password from json file : {}").format(str(e)))
load_password()

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

class LoginForm(FlaskForm):
    """
        Login form for WTF
    """
    username = StringField("username",validators=[DataRequired()])
    password = PasswordField("password",validators=[DataRequired()])
    submit = SubmitField(label=_("登录"))

class RegisterForm(FlaskForm):
    """
        Registration form for WTF
    """
    username = StringField("username",validators=[DataRequired()])
    password = PasswordField("password",validators=[DataRequired()])
    v_password = PasswordField("v_password",validators=[DataRequired()])

@app.route("/login" , methods=["POST","GET"])
@app.route("/login/" , methods=["POST","GET"])
@app.route("/login.html", methods=["POST","GET"])
def login():
    """
        Login
    """
    login_form = LoginForm()
    if request.method == 'POST':
        username = login_form.username.data
        password = login_form.password.data
        if username is None or password is None:
            log.loge(_("Empty username or password"))
            return render_template("login.html",error=_("Username and password is required"))
        user_info = get_user(username)
        if user_info is None:
            return render_template("login.html" , error = _("User is not found in the database"))
        else:
            user = User(user_info)
            if user.verify_password(password):  # 校验密码
                login_user(user)
                log.log(_("User login successful"))
                return redirect('/desktop')
    return render_template('login.html',form=login_form)

@app.route("/logout", methods=["GET"])
@app.route("/logout/" , methods=["GET"])
@app.route("/logout.html", methods=["GET"])
@login_required
def logout():
    logout_user()
    log.logd(_("User has been logged out"))
    return redirect('/')

@app.route("/register", methods=["GET","POST"])
@app.route("/register/", methods=["GET","POST"])
@app.route("/register.html", methods=["GET","POST"])
def register():
    """
        Register a new account and return a redirect
    """
    register_form = RegisterForm()
    if request.method == 'POST':
        username = register_form.username.data
        password = register_form.password.data
        v_password = register_form.v_password.data

        error = ""
        info = ""

        if username is None:
            log.loge(_("Username is required"))
            error = _("Username is required")
        else:
            user_info = get_user(username)
            # Check if the user is already existing
            if user_info is not None:
                return render_template("login.html", info = _("Username had already registered , try to login"))
            # Check if the password is null
            elif password is None or v_password is None:
                error = _("Password is required")
            elif password != v_password:
                error = _("Password is not same")
            global USERS
            USERS.append({"id" : len(USERS) + 1 , "username" : username, "password" : generate_password_hash(password)})
            info = _("User registered successfully")
            # Save the password to a file right now to avoid overwriting
            try:
                with open(os.path.join(os.getcwd(), "config" , "password.json"),mode="w+",encoding="utf-8") as f:
                    f.write(json.dump(USERS,indent=4))
            except json.JSONDecodeError as e:
                log.loge(_("Error decoding password to json file : {}").format(str(e)))
            except OSError as e:
                log.loge(_("Failed to save password to json file : {}").format(str(e)))
            return render_template("register.html", error = error , info = info)
    return render_template('register.html')

@app.route("/forget-password",methods=["GET","POST"])
@app.route("/forget-password/",methods=["GET","POST"])
@app.route("/forget-password.html",methods=["GET","POST"])
def forget_password():
    return render_template("forget-password.html")

# Disable Flask logging system
if not c.config.get('debug'):
    logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.ERROR)
# Disable waitress logging system
logger = logging.getLogger('waitress')
logger.setLevel(logging.ERROR)

import server.config as c

from server.web.webpage import create_html_page
create_html_page(app)
from server.web.webindi import create_indiweb_manager
create_indiweb_manager(app,csrf)
from server.web.websys import create_web_sysinfo
create_web_sysinfo(app)
from server.web.webtools import create_web_tools
create_web_tools(app)
from server.web.webdevice import create_indimanager_html
create_indimanager_html(app,csrf)
from server.web.websearch import create_search_template
create_search_template(app,csrf)

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
        