import multiprocessing
import socket
import logging
import json
from urllib.parse import unquote_plus
from http_handler import HttpHandler
from http.server import HTTPServer
from pymongo.mongo_client import MongoClient


def save_data(config, data):
    client = MongoClient(config["DB"]["uri"])
    db = client.homework
    parse_data = unquote_plus(data.decode())
    try:
        parse_data = {
            key: value for key, value in [el.split("=") for el in parse_data.split("&")]
        }
        db.messages.insert_one(parse_data)
    except ValueError as e:
        logging.error(f"Parse error: {e}")
    except Exception as e:
        logging.error(f"Failed to save: {e}")
    finally:
        client.close()


def run_http_server(config):
    http_server = HTTPServer(
        (config["HTTP_SERVER"]["host"], config["HTTP_SERVER"]["port"]), HttpHandler
    )

    try:
        logging.info(
            f"Server started on http://{config['HTTP_SERVER']['host']}:{config['HTTP_SERVER']['port']}"
        )
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
    except Exception as e:
        logging.error(f"Server error: {e}")
    finally:
        logging.info("Http server stopped")
        http_server.server_close()


def run_server(config):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((config["SOCKET_SERVER"]["host"], config["SOCKET_SERVER"]["port"]))
    logging.info(
        f"Socket server started on socket://{config['SOCKET_SERVER']['host']}:{config['SOCKET_SERVER']['port']}"
    )

    try:
        while True:
            data, addr = sock.recvfrom(config["SOCKET_SERVER"]["buffer_size"])
            logging.info(f"Get message from {addr}: {data.decode()}")
            save_data(config, data)
    except Exception as e:
        logging.error(f"Server error: {e}")
    finally:
        logging.info("Server stopped")
        sock.close()


def start_http_server(config):
    run_http_server(config)


def start_socket_server(config):
    run_server(config)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(threadName)s - %(message)s"
    )

    try:
        config = json.load(open("config.json"))
    except FileNotFoundError:
        logging.error(f"Error while opening config.json. Using default values.")

    http_server_process = multiprocessing.Process(
        target=start_http_server,
        args=(config,),
    )
    http_server_process.start()

    socket_server = multiprocessing.Process(
        target=start_socket_server,
        args=(config,),
    )
    socket_server.start()

    http_server_process.join()
    socket_server.join()
