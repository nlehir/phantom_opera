import json
import logging
import os
import random
import socket
from logging.handlers import RotatingFileHandler

from src.network import Protocol

host = "localhost"
port = 12000
# HEADERSIZE = 10

"""
set up fantom logging
"""
fantom_logger = logging.getLogger()
fantom_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")


# # file
# if os.path.exists("./logs/fantom.log"):
#     os.remove("./logs/fantom.log")
# file_handler = RotatingFileHandler('./logs/fantom.log', 'a', 1000000, 1)
# file_handler.setLevel(logging.DEBUG)
# file_handler.setFormatter(formatter)
# fantom_logger.addHandler(file_handler)
# # stream
# stream_handler = logging.StreamHandler()
# stream_handler.setLevel(logging.WARNING)
# fantom_logger.addHandler(stream_handler)


class Player():

    def __init__(self):

        self.end = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self):
        self.socket.connect((host, port))

    def reset(self):
        self.socket.close()

    def answer(self, question):
        # work
        data = question["data"]
        game_state = question["game state"]
        response_index = random.randint(0, len(data)-1)
        # log
        fantom_logger.debug("|\n|")
        fantom_logger.debug("fantom answers")
        fantom_logger.debug(f"question type ----- {question['question type']}")
        fantom_logger.debug(f"data -------------- {data}")
        fantom_logger.debug(f"response index ---- {response_index}")
        fantom_logger.debug(f"response ---------- {data[response_index]}")
        return response_index

    def handle_json(self, data):
        data = json.loads(data)
        response = self.answer(data)
        # send back to server
        bytes_data = json.dumps(response).encode("utf-8")
        Protocol.send(self.socket, bytes_data)

    def authenticate(self):
        print("Trying to authenticate", flush=True)
        Protocol.send_string(self.socket, "fantom connection random@epitech.eu")
        print("Asked for authentication", flush=True)
        auth_resp = Protocol.receive_string(self.socket)
        print("Received response : " + auth_resp, flush=True)

        if not auth_resp == "connection accepted":
            self.reset()
            return False
        return True

    def run(self):
        print("Trying to connect")
        self.connect()
        print("Connected")

        if not self.authenticate():
            return

        while self.end is not True:
            received_message = Protocol.receive(self.socket)
            if received_message:
                self.handle_json(received_message)
            else:
                print("no message, finished learning")
                self.end = True


p = Player()

p.run()
