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

from server.wsserver import run_server,run_ws_server
from utils.lightlog import lightlog

log = lightlog(__name__)

import gettext
_ = gettext.gettext
import threading

version = "1.0.0"

if __name__ == "__main__":
    log.log(_("Initialize LightAPT server ..."))
    log.log(_(f"Current version is {version}"))

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5001)
    parser.add_argument('--host', type=str, default='127.0.0.1')
    parser.add_argument('--wport', type=int, default=5000)
    parser.add_argument('--whost', type=str, default='127.0.0.1')
    parser.add_argument('--debug', type=bool, default=False)
    parser.add_argument('--config', type=str, default='')
    args = parser.parse_args()
    if args.debug:
        """Debug mode"""
    if args.config:
        """Change configuration file"""    
    try:
        server_thread = threading.Thread(target=run_server,kwargs={"host" : args.host , "port" : args.port})
        server_thread.daemon = True
        server_thread.start()

        ws_server_thread = threading.Thread(target=run_ws_server,kwargs={"host" : args.whost , "port" : args.wport})
        ws_server_thread.daemon = True
        ws_server_thread.start()
        
        log.log(_("LightAPT server started."))
        ws_server_thread.join()
    except KeyboardInterrupt as exception:
        log.log(_("Shutdown lightAPT server by user"))
else:
    log.loge(_("Please run this file in main thread"))
    raise SystemError("Main Thread")