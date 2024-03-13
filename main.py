import mimetypes
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import multiprocessing


class HttpHandler(BaseHTTPRequestHandler):
    async def do_POST(self):
        data = await self.rfile.read(int(self.headers["Content-Length"]))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }
        print(data_dict)
        await self.send_response(302)
        await self.send_header("Location", "/")
        await self.end_headers()

    async def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            await self.send_html_file("index.html")
        elif pr_url.path == "/contact":
            await self.send_html_file("contact.html")
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                await self.send_static()
            else:
                await self.send_html_file("error.html", 404)

    async def send_html_file(self, filename, status=200):
        await self.send_response(status)
        await self.send_header("Content-type", "text/html")
        await self.end_headers()
        async with open(filename, "rb") as fd:
            await self.wfile.write(fd.read())

    async def send_static(self):
        await self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            await self.send_header("Content-type", mt[0])
        else:
            await self.send_header("Content-type", "text/plain")
        await self.end_headers()
        async with open(f".{self.path}", "rb") as file:
            await self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def run_http_server(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def start_http_server():
    run_http_server()


def start_socket_server():
    pass


if __name__ == "__main__":
    http_server_process = multiprocessing.Process(target=start_http_server)
    http_server_process.start()

    # socket_server = multiprocessing.Process(target=start_socket_server)
    # socket_server.start()

    http_server_process.join()
    # socket_server.join()
