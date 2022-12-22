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

from server.webapp import run_server
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
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--host', type=str, default='127.0.0.1')
    parser.add_argument('--debug', type=bool, default=False)
    parser.add_argument('--config', type=str, default='')
    parser.add_argument('--gui' , type=bool, default= False)
    args = parser.parse_args()    
    
    if args.debug:
        """Debug mode"""
    if args.config:
        """Change configuration file"""    
    if args.gui:
        """Open terminal ui based on """
    try:
        run_server(args.host, args.port,False)

    except KeyboardInterrupt as exception:
        log.log(_("Shutdown lightAPT server by user"))
else:
    log.loge(_("Please run this file in main thread"))
    raise SystemError("Main Thread")