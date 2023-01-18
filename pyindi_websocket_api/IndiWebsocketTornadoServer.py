import asyncio
import tornado.web
import tornado.websocket
from Indi_websocket_interface import *


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class EchoWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print("WebSocket closed")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/ws/echo/", EchoWebSocket),
        (r"/ws/debugging/", DebuggingWebSocket),
        (r"/ws/indi_client/", IndiClientWebSocket),
        (r"/FIFO/([^/]+)/([^/]+)/([^/]+)/", FIFODeviceStartStop),
    ])


async def main():
    app = make_app()
    app.listen(7999)
    shutdown_event = asyncio.Event()
    await shutdown_event.wait()


if __name__ == "__main__":
    asyncio.run(main())