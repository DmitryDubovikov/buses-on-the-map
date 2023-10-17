import json

import trio
from trio_websocket import ConnectionClosed, serve_websocket, WebSocketConnection

buses = {}


async def buses_server(request):
    ws = await request.accept()
    while True:
        try:
            message = json.loads(await ws.get_message())

            print(f"server received message: {message}")
            bus_id = message["busId"]
            buses[bus_id] = {
                "lat": message["lat"],
                "lng": message["lng"],
                "route": message["route"],
            }
            await ws.send_message("OK, thanks")
        except ConnectionClosed:
            break


async def send_buses(ws: WebSocketConnection):
    buses_coord_snapshot = []
    for bus, bus_details in buses.items():
        buses_coord_snapshot.append(
            {
                "busId": bus,
                "lat": bus_details["lat"],
                "lng": bus_details["lng"],
                "route": bus_details["route"],
            }
        )
    reply_message = {
        "msgType": "Buses",
        "buses": buses_coord_snapshot,
    }
    await ws.send_message(json.dumps(reply_message, ensure_ascii=True))


async def listen_to_browser(ws: WebSocketConnection):
    await trio.sleep(0)


async def speak_to_browser(ws: WebSocketConnection):
    while True:
        await trio.sleep(0.1)
        await send_buses(ws)


async def browser_server(request):
    async with trio.open_nursery() as nursery:
        ws = await request.accept()
        nursery.start_soon(listen_to_browser, ws)
        nursery.start_soon(speak_to_browser, ws)


async def main():
    async with trio.open_nursery() as nursery:
        nursery.start_soon(serve_websocket, browser_server, "127.0.0.1", 8000, None)
        nursery.start_soon(serve_websocket, buses_server, "127.0.0.1", 8080, None)


if __name__ == "__main__":
    trio.run(main)
