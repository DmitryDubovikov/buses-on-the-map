import json

import trio
from trio_websocket import ConnectionClosed, serve_websocket


async def buses_server(request):
    web_socket = await request.accept()
    while True:
        try:
            message = json.loads(await web_socket.get_message())
            print(f"server received message: {message}")
            await web_socket.send_message("OK, thanks")
        except ConnectionClosed:
            break


async def main():
    await serve_websocket(buses_server, "127.0.0.1", 8080, ssl_context=None)


if __name__ == "__main__":
    trio.run(main)
