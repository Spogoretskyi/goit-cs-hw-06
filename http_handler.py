import mimetypes
import pathlib
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler


class HttpHandler(BaseHTTPRequestHandler):
    def __init__(self, logger):
        self.logger = logger

    async def do_POST(self):
        data = await self.rfile.read(int(self.headers["Content-Length"]))
        self.logger.info(
            f"POST request: Path: {self.path}; Headers: {self.headers}; Body: {data.decode()}"
        )
        data_parse = urllib.parse.unquote_plus(data.decode())
        self.logger.info(
            f"POST request: Path: {self.path}; Headers: {self.headers}; Body: {data_parse}"
        )
        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }
        await self.send_response(302)
        await self.send_header("Location", "/")
        await self.end_headers()

    async def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        self.logger.info(
            f"GET request: Path: {self.path}; Headers: {self.headers}; Query: {pr_url.query}"
        )
        if pr_url.path == "/":
            self.logger.info(f"GET request: index: {pr_url}")
            await self.send_html_file("index.html")
        elif pr_url.path == "/contact":
            self.logger.info(f"GET request: contact: {pr_url}")
            await self.send_html_file("contact.html")
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                await self.send_static()
            else:
                self.logger.info(f"GET request: URL error: {pr_url}")
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
