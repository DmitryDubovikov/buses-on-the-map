import json
import trio
import os
from sys import stderr
from trio_websocket import open_websocket_url
from itertools import cycle


def load_routes(directory_path="routes"):
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, "r", encoding="utf8") as file:
                yield json.load(file)


async def send_bus_route(route):
    try:
        async with open_websocket_url("ws://127.0.0.1:8080") as ws:
            for point in cycle(route["coordinates"]):
                message = {
                    "busId": route["name"],
                    "lat": point[0],
                    "lng": point[1],
                    "route": route["name"],
                }
                await ws.send_message(json.dumps(message, ensure_ascii=True))
                message = await ws.get_message()
                print(f"fake bus received message: {message}")
                await trio.sleep(0.1)
    except OSError as e:
        print(f"Connection attempt failed: {e}", file=stderr)


async def main():
    async with trio.open_nursery() as nursery:
        for route in load_routes():
            nursery.start_soon(send_bus_route, route)


if __name__ == "__main__":
    trio.run(main)
