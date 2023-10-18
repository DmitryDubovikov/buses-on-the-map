import json
import logging
from functools import partial

import configargparse
import trio
from trio_websocket import ConnectionClosed, serve_websocket

logger = logging.getLogger(__file__)
HOST = "127.0.0.1"
LISTEN_BUSES_PORT = 8080
LISTEN_BROWSERS_PORT = 8000

buses = {}


class Bus:
    def __init__(self, bus):
        self.bus_id = bus["busId"]
        self.lat = bus["lat"]
        self.lng = bus["lng"]
        self.route = bus["route"]

    def to_dict(self):
        return {
            "busId": self.bus_id,
            "lat": self.lat,
            "lng": self.lng,
            "route": self.route,
        }


class WindowBound:
    def __init__(self, bound):
        self.east_lng = bound["east_lng"]
        self.north_lat = bound["north_lat"]
        self.south_lat = bound["south_lat"]
        self.west_lng = bound["west_lng"]

    def is_inside(self, bus):
        if not self.south_lat < bus.lat < self.north_lat:
            return False
        if not self.west_lng < bus.lng < self.east_lng:
            return False
        return True

    def update(self, bound):
        self.east_lng = bound["east_lng"]
        self.north_lat = bound["north_lat"]
        self.south_lat = bound["south_lat"]
        self.west_lng = bound["west_lng"]


async def send_buses(ws, shared_bound):
    visible_buses = []
    for _, bus in buses.items():
        if shared_bound.is_inside(bus):
            visible_buses.append(bus.to_dict())
    reply_message = {
        "msgType": "Buses",
        "buses": visible_buses,
    }
    await ws.send_message(json.dumps(reply_message, ensure_ascii=True))


async def listen_browser(ws, shared_bound):
    while True:
        bound_message = json.loads(await ws.get_message())
        logger.debug("Recived message: %s", bound_message)
        logger.debug("New bound message is received. Processing...")
        shared_bound.update(bound_message["data"])


async def talk_to_browser(ws, shared_bound):
    while True:
        await trio.sleep(1)
        await send_buses(ws, shared_bound)


async def browser_server(request):
    ws = await request.accept()
    logger.debug("Open connection on browsers port")
    try:
        async with trio.open_nursery() as nursery:
            shared_bound = WindowBound(
                {
                    "east_lng": 0,
                    "north_lat": 0,
                    "south_lat": 0,
                    "west_lng": 0,
                }
            )
            nursery.start_soon(listen_browser, ws, shared_bound)
            nursery.start_soon(talk_to_browser, ws, shared_bound)
    except ConnectionClosed:
        logger.debug("Close connection on browsers port")


async def buses_server(request):
    ws = await request.accept()
    while True:
        try:
            bus_message = json.loads(await ws.get_message())
            for bus in bus_message["buses"]:
                bus_id = bus["busId"]
                buses[bus_id] = Bus(bus)
            await ws.send_message("OK")
        except ConnectionClosed:
            break


listen_buses_coord_ws = partial(
    serve_websocket,
    buses_server,
    HOST,
    LISTEN_BUSES_PORT,
    ssl_context=None,
)

listen_browsers_ws = partial(
    serve_websocket,
    browser_server,
    HOST,
    LISTEN_BROWSERS_PORT,
    ssl_context=None,
)


async def main():
    parser = configargparse.ArgParser()
    parser.add(
        "-host",
        required=False,
        help="host to connection",
        env_var="HOST",
        default="127.0.0.1",
    )
    parser.add(
        "-browser_port",
        required=False,
        help="host to connection",
        env_var="BROWSER_PORT",
        default="8000",
    )
    parser.add(
        "-bus_port",
        required=False,
        help="buses server port",
        env_var="BUSES_SERVER_PORT",
        default="8080",
    )

    options = parser.parse_args()

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.debug(options)
    async with trio.open_nursery() as nursery:
        nursery.start_soon(listen_buses_coord_ws)
        nursery.start_soon(listen_browsers_ws)


if __name__ == "__main__":
    try:
        trio.run(main)
    except KeyboardInterrupt:
        logger.debug("Exit by Ctrl-C!")
