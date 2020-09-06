import json
import time
from logging import Logger
from socket import socket

from src.game.PlayerType import PlayerType
from src.network import Protocol


class Client:
    sock: socket
    isConnected: bool
    isAuthenticated: bool
    playerType: PlayerType
    threadId: int
    logger: Logger

    def __init__(self, sock: socket, threadId: int, logger: Logger):
        self.sock = sock
        self.threadId = threadId
        self.isConnected = True
        self.isAuthenticated = False
        self.logger = logger
        self.playerType = PlayerType.UNDEFINED

    def disconnect(self):
        self.isConnected = False

    def handle_messages(self):
        """
            This is actually used to handle the authentication and know the type of client connecting
            In later versions it should hold all the receiving from a client and put messages into queue
            But for now this will do well
        """
        while self.isConnected:
            time.sleep(1)
            if not self.isAuthenticated:
                self.logger.info("Waiting for authentication of user : " + str(self.threadId))
                received = Protocol.receive_json(self.sock)
                msg = json.loads(received)
                if msg == "inspector connection":
                    self.isAuthenticated = True
                    self.playerType = PlayerType.INSPECTOR
                if msg == "inspector connection":
                    self.isAuthenticated = True
                    self.playerType = PlayerType.FANTOM
                if self.isAuthenticated:
                    self.logger.info(str(self.threadId) + ": Authentication accepted, Welcome !")
                else:
                    self.logger.info(str(self.threadId) + ": Authentication refused, Sorry !")
