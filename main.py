from ws_connection import ClientClosedError
from ws_server import WebSocketServer, WebSocketClient
import network
import machine
import neopixel
import time

np = neopixel.NeoPixel(machine.Pin(27), 50)


def hex_to_rgb(hex):
    rgb = []
    for i in (1, 3, 5):
        decimal = int(hex[i:i+2], 16)
        rgb.append(decimal)

    return tuple(rgb)


class TestClient(WebSocketClient):
    def __init__(self, conn):
        super().__init__(conn)

    def process(self):
        try:
            msg = self.connection.read()
            if not msg:
                return
            msg = msg.decode("utf-8")
            items = msg.split(" ")
            cmd = items[0]
            if cmd == "Hello":
                self.connection.write(cmd + " World")
                print("Hello World")
            if cmd == "change_color":
                color = hex_to_rgb(items[1])
                print("Changing colour to ", color)
                for i in range(np.n):
                    np[i] = color
                np.write()
        except ClientClosedError:
            self.connection.close()


class TestServer(WebSocketServer):
    def __init__(self):
        super().__init__("main.html", 2)

    def _make_client(self, conn):
        return TestClient(conn)


ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="mpy_00001", password="foo")
print('Network config:', ap.ifconfig())

server = TestServer()
server.start()
try:
    while True:
        server.process_all()
except KeyboardInterrupt:
    pass
server.stop()
