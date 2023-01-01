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

from server.webapp import run_server,set_configration
from utils.lightlog import lightlog,DEBUG
import argparse,threading,os
log = lightlog(__name__)

version = "1.0.0"

from utils.i18n import _

def main():
    """
        Main function | 主函数
        Args : None
        Return : None
    """
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000,help=_("Port the server is listening on"))
    parser.add_argument('--host', type=str, default='0.0.0.0',help=_("Host the server is listening on"))
    parser.add_argument('--debug', type=bool, default=False,help=_("Enable debug output for better debug"))
    parser.add_argument('--threaded', type=bool, default=True,help=_("Enable mutiline threading for better performance"))
    parser.add_argument('--config', type=str, default=os.path.join(os.getcwd(), 'config',"config.json"),help=_("Config file"))
    parser.add_argument('--gui' , type=bool, default= False,help=_("Use GUI to set the configurations"))
    parser.add_argument('--version', type=bool, default=False,help=_("Show current version"))
    parser.add_argument('--indiweb' , type=bool,default=False,help=_("Whether to start the INDI web manager"))
    parser.add_argument('--indihost',type=str,default="0.0.0.0",help=_("The host where the INDI web manager is running"))
    parser.add_argument('--indiport', type=int,default=8624,help=_("The port where the INDI web manager is running"))
    parser.add_argument('--indipport', type=int,default=7624,help=_("The port where the INDI server is running"))
    parser.add_argument('--indiconfig', type=str,default="/tmp/indi",help=_("The path of the INDI temp files"))
    parser.add_argument('--indidata', type=str,default="/usr/share/indi",help=_("The path of the INDI data files"))
    parser.add_argument('--indififo', type=str,default="/tmp/indiFIFO",help=_("The path of the INDI fifo pipe"))
    args = parser.parse_args()    

    if args.version:
        log.log(_("Current version is {}").format(version))
        exit()
    if args.debug:
        """Debug mode"""
        global DEBUG
        DEBUG = args.debug
    if args.config:
        """Change configuration file"""
        set_configration(args.config)
    if args.gui:
        """Open terminal ui based on """

    if args.indiweb:
        from server.indiweb.webapp import start_indiweb
        indiweb_thread = threading.Thread(target=start_indiweb,kwargs={
            "host": args.indihost,
            "port": args.indiport,
            "indi_port": args.indipport,
            "fifo_path": args.indififo,
            "config_path": args.indiconfig,
            "data_path": args.indidata,
        })
        # 设置主线程同步，但是由于python3.10.6的语法修改，是的需要进行判断
        try:
            indiweb_thread.daemon = True
        except DeprecationWarning:
            indiweb_thread.setDaemon(True)
        log.log(_("Starting INDI web manager on {}:{}").format(args.indihost,args.indiport))
        indiweb_thread.start()
    log.log(_("Initialize LightAPT server ..."))
    log.log(_("Current version is {}").format(version))
    try:
        run_server(args.host, args.port,args.threaded,args.debug)
    except KeyboardInterrupt:
        log.log(_("Shutdown lightAPT server by user"))

if __name__ == "__main__":
    main()