import json
import os
import random
from itertools import cycle, islice
from sys import stderr

import trio
from trio_websocket import open_websocket_url


def load_routes(directory_path="routes"):
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, "r", encoding="utf8") as file:
                yield json.load(file)


def generate_bus_id(route_id, bus_index):
    return f"{route_id}-{bus_index}"


async def run_bus(ws, route, bus_index):
    route_points = route["coordinates"]
    bus_id = generate_bus_id(route["name"], bus_index)
    cycle_route = cycle(route_points)
    length_route = len(route_points)
    random_start_point = random.randint(1, length_route)
    for point in islice(cycle_route, random_start_point, None):
        message = {
            "busId": f"{route['name']}-{bus_id}",
            "lat": point[0],
            "lng": point[1],
            "route": route["name"],
        }
        await ws.send_message(json.dumps(message, ensure_ascii=True))
        message = await ws.get_message()
        print(f"fake bus received message: {message}")
        await trio.sleep(0.1)


async def send_bus_route(route):
    try:
        async with open_websocket_url("ws://127.0.0.1:8080") as ws:
            async with trio.open_nursery() as nursery:
                for i in range(5):
                    nursery.start_soon(run_bus, ws, route, i)

    except OSError as e:
        print(f"Connection attempt failed: {e}", file=stderr)


async def main():
    async with trio.open_nursery() as nursery:
        for route in load_routes():
            nursery.start_soon(send_bus_route, route)


if __name__ == "__main__":
    trio.run(main)
