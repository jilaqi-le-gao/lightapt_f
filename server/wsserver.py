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

import os
from utils.lightlog import lightlog
log = lightlog(__name__)
import gettext
_ = gettext.gettext

from flask import Flask,render_template

app = Flask(__name__,
    static_folder=os.path.join(os.getcwd(),os.path.join("client","static")),
    template_folder=os.path.join(os.getcwd(),os.path.join("client","templates"))
)
thread = None
server = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/main.html')
def main():
    return render_template('main.html')

@app.route('/novnc')
def novnc():
    return render_template('novnc.html')

def run_server(host : str , port : int) -> None:
    """
        Start the server | 启动服务器
        Args: 
            host : str # default is "127.0.0.1"
            port : int # default is 5001
        Return: None
    """
    app.run(host=host, port=port,debug=True)
