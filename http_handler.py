import mimetypes
import pathlib
import urllib.parse
import logging
import json
import socket
from http.server import BaseHTTPRequestHandler


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            config = json.load(open("config.json"))
        except FileNotFoundError:
            logging.error(f"Error while opening config.json. Using default values.")

        size = self.headers.get("Content-Length")
        data = self.rfile.read(int(size)).decode()
        logging.info(
            f"POST request: Path: {self.path}; Headers: {self.headers}; Data: {data}"
        )

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(
            data.encode(),
            (
                config["SOCKET_SERVER"]["host"],
                config["SOCKET_SERVER"]["port"],
            ),
        )
        client_socket.close()

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        logging.info(
            f"GET request: Path: {self.path}; Headers: {self.headers}; Query: {pr_url.query}"
        )
        if pr_url.path == "/":
            logging.info(f"GET request: index: {pr_url}")
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            logging.info(f"GET request: message: {pr_url}")
            self.send_html_file("message.html")
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                logging.info(f"GET request: URL error: {pr_url}")
                self.send_html_file("error.html", 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())
