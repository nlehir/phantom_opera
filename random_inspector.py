import json
import random
import socket
from threading import Thread

import protocol


class Player(Thread):
    def __init__(self):
        super().__init__()
        self.end = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self):
        self.socket.connect(("localhost", 12000))

    def reset(self):
        self.socket.close()

    def answer(self, question):
        # work
        data = question["data"]
        response_index = random.randint(0, len(data) - 1)
        return response_index

    def handle_json(self, data):
        data = json.loads(data)
        if data['question type'] == 'END':
            return 1
        response = self.answer(data)
        # send back to server
        bytes_data = json.dumps(response).encode("utf-8")
        protocol.send_json(self.socket, bytes_data)
        return 0

    def run(self):

        self.connect()

        while self.end is not True:
            received_message = protocol.receive_json(self.socket)
            if received_message:
                if self.handle_json(received_message) == 1:
                    self.end = True

            else:
                print("no message, finished learning")
                self.end = True
