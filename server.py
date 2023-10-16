import json

import trio
from trio_websocket import ConnectionClosed, serve_websocket

TEST_MESSAGE = {
    "msgType": "Buses",
    "buses": [
        {"busId": "156", "lat": 55.7500, "lng": 37.600, "route": "156"},
    ],
}


async def read_coordinates_from_json(filename):
    with open(filename, "r") as file:
        data = json.load(file)
        coordinates = data.get("coordinates", [])

        for coordinate in coordinates:
            yield coordinate
            await trio.sleep(1)


async def echo_server(request):
    filename = "156.json"

    ws = await request.accept()
    while True:
        try:
            # message = await ws.get_message()
            # message = json.dumps(TEST_MESSAGE)

            async for coordinate in read_coordinates_from_json(filename):
                TEST_MESSAGE["buses"][0]["lat"] = coordinate[0]
                TEST_MESSAGE["buses"][0]["lon"] = coordinate[1]

                message = json.dumps(TEST_MESSAGE)
                await ws.send_message(message)
        except ConnectionClosed:
            break


async def main():
    await serve_websocket(echo_server, "127.0.0.1", 8000, ssl_context=None)


if __name__ == "__main__":
    trio.run(main)
