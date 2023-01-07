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

import argparse,os,json

import server.config as c
from utils.i18n import _
from utils.lightlog import lightlog,DEBUG
logger = lightlog(__name__)

def main():
    """
        Main function | 主函数
        Args : None
        Return : None
    """
    # Load configuration from file
    try:
        with open(os.path.join(os.getcwd(),"config","config.json"),mode="r",encoding="utf-8") as f:
            c.config = json.load(f)
    except FileNotFoundError as e:
        logger.loge(_("Config file not found : {}").format(str(e)))
    except json.JSONDecodeError as e:
        logger.loge(_("Config file is not valid : {}").format(str(e)))
    except:
        logger.loge(_("Unknown error while reading config file : {}").format(str(e)))

    # Command line arguments
    parser = argparse.ArgumentParser()
    # Server options
    parser.add_argument('--port', type=int, default=8000,help=_("Port the server is listening on"))
    parser.add_argument('--host', type=str, default='0.0.0.0',help=_("Host the server is listening on"))
    parser.add_argument('--debug', type=bool, default=False,help=_("Enable debug output for better debug"))
    parser.add_argument('--threaded', type=bool, default=True,help=_("Enable mutiline threading for better performance"))
    # Configuration and version
    parser.add_argument('--config', type=str, default=os.path.join(os.getcwd(), 'config',"config.json"),help=_("Config file"))
    parser.add_argument('--version', type=bool, default=False,help=_("Show current version"))
    # Websocket server options
    parser.add_argument('--wsport', type=int, default=5000,help=_("Websocket server port"))
    parser.add_argument('--wshost', type=str, default='0.0.0.0',help=_("Websocket server host"))
    parser.add_argument('--wsssl',type=bool, default=False,help=_("Websocket SSL mode"))
    parser.add_argument('--wskey',type=str,default='',help=_("Websocket SSL key"))
    parser.add_argument('--wscert',type=str,default='',help=_("Websocket SSL certificate"))
    # INDI web manager options
    parser.add_argument('--indiweb' , type=bool,default=True,help=_("Start the INDI web manager"))
    parser.add_argument('--indihost',type=str,default="127.0.0.1",help=_("INDI server address"))
    parser.add_argument('--indiport', type=int,default=7624,help=_("The port where the INDI server is running"))
    parser.add_argument('--indiconfig', type=str,default="/tmp/indi",help=_("The path of the INDI temp files"))
    parser.add_argument('--indidata', type=str,default="/usr/share/indi",help=_("The path of the INDI data files"))
    parser.add_argument('--indififo', type=str,default="/tmp/indiFIFO",help=_("The path of the INDI fifo pipe"))
    parser.add_argument('--indiauto', type=bool,default=False,help=_("Connect to the INDI device when server is started"))

    args = parser.parse_args()
    # Change the host if the command line argument is specified
    if args.host:
        _host = args.host
        if not isinstance(_host,str):
            logger.loge(_("Invalid host"))
        c.config["host"] = _host
        logger.log(_("Server host : {}").format(_host))
    # Change the port if the command line argument is specified
    if args.port:
        _port = int(args.port)
        if not isinstance(_port,int):
            logger.loge(_("Invalid port"))
        c.config["port"] = _port
        logger.log(_("Server port : {}").format(_port))
    # Change the debug mode if available
    if args.debug:
        """Debug mode"""
        global DEBUG
        DEBUG = args.debug
        logger.log(_("DEBUG mode is enabled"))
    # Change the threaded mode if available
    if args.threaded:
        """Threaded mode"""
        c.config["threaded"] = args.threaded
        logger.log(_("Threaded mode is enabled"))
    # Change the INDI web manager options if available
    try:
        if args.indihost:
            c.config["indiweb"]["host"] = args.indihost
            logger.log(_("INDI server host : {}").format(c.config["indiweb"]["host"]))
        if args.indiport:
            c.config["indiweb"]["port"] = args.indiport
            logger.log(_("INDI server port : {}").format(c.config["indiweb"]["port"]))
        if args.indidata:
            c.config["indiweb"]["data"] = args.indidata
            logger.log(_("INDI data path : {}").format(c.config["indiweb"]["data"]))
        if args.indififo:
            c.config["indiweb"]["fifo"] = args.indififo
            logger.log(_("INDI fifo pipe path : {}").format(c.config["indiweb"]["fifo"]))
        try:
            c.config["indiweb"]["config"] = os.path.join(os.environ['HOME'], '.indi')
        except KeyError:
            c.config["indiweb"]["config"] = '/tmp/indi'
    except KeyError as e:
        logger.loge(_("Invalid INDI web manager options : {}").format(str(e)))
    # Start the web server
    try:
        from server.wsserver import ws_server
        _ws_ = ws_server()
        _ws_.start_server(c.config["ws"]["host"], c.config["ws"]["port"], c.config["ws"]["ssl"],c.config["ws"]["key"], c.config["ws"]["cert"])
        from server.webapp import run_server
        run_server()
    except KeyboardInterrupt:
        logger.log(_("Shutdown LightAPT server by user"))

if __name__ == "__main__":
    main()