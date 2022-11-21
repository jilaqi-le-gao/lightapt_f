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
import json
import gettext
_ = gettext.gettext

import asyncio
import websockets
 
IP_ADDR = "127.0.0.1"
IP_PORT = "8888"

async def on_connect(websocket):
    """"""
    while True:
        recv_text = await websocket.recv()
        if recv_text == "hello":
            print("connected success")
            await websocket.send("123")
            return True
        else:
            await websocket.send("connected fail")

async def on_listening(websocket,path):
    """"""
    

async def run():
    log.log(_(f"Start websocket server on {IP_PORT} at {IP_ADDR}"))
    server = websockets.serve(on_listening, IP_ADDR, IP_PORT)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()