import mimetypes
import pathlib
import urllib.parse
import multiprocessing
from http.server import HTTPServer, BaseHTTPRequestHandler
from server import Server
from http_handler import HttpHandler


async def run_http_server(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("localhost", 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


async def run_server(logger, server_class=HTTPServer, handler_class=HttpHandler):
    server = Server(logger)
    async with websockets.serve(server.ws_handler, "localhost", 5000):
        try:
            await asyncio.Future()
        except KeyboardInterrupt:
            server.unregister()
    asyncio.run(serve())


async def start_http_server():
    await run_http_server()


async def start_socket_server():
    await run_server()


if __name__ == "__main__":
    http_server_process = multiprocessing.Process(target=start_http_server)
    http_server_process.start()

    socket_server = multiprocessing.Process(target=start_socket_server)
    socket_server.start()

    http_server_process.join()
    socket_server.join()
