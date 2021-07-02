import errno
import time
from logging import Logger
import socket
from threading import Thread
from typing import List

from src.game.PlayerType import PlayerType
from src.network import Protocol
from src.utils import email_utils
from src.utils.globals import remove_waiting_client, clients


class Client:
    sock: socket
    isConnected: bool
    isAuthenticated: bool
    isPlaying: bool
    playerType: PlayerType
    username: str
    clientId: int
    logger: Logger
    hasWon: bool
    clientAuthenticationThread: Thread

    def __init__(self, sock: socket, threadId: int, logger: Logger):
        self.sock = sock
        self.clientId = threadId
        self.isConnected = True
        self.isAuthenticated = False
        self.isPlaying = False
        self.logger = logger
        self.playerType = PlayerType.UNDEFINED
        self.hasWon = False
        self.clientAuthenticationThread = Thread(target=self.handle_messages)
        self.clientAuthenticationThread.start()

    def disconnect(self):
        self.isConnected = False
        self.sock.close()
        if self.clientAuthenticationThread.is_alive():
            self.clientAuthenticationThread.join()
        if not self.isPlaying:
            remove_waiting_client(self)

    def refuse_connection(self):
        Protocol.send_string(self.sock, "connection refused")
        self.logger.info(str(self.clientId) + ": Authentication refused, Sorry !")
        self.disconnect()

    def accept_connection(self, client_type: PlayerType, username: str):
        self.isAuthenticated = True
        self.playerType = client_type
        self.username = username

    def check_authentication(self, tokens: List[str], client_type: PlayerType):
        if tokens[1] == "connection" and email_utils.valid_email(tokens[2]):
            self.accept_connection(client_type, tokens[2])
        else:
            self.refuse_connection()

    def handle_messages(self):
        """
            This is actually used to handle the authentication and know the type of client connecting
            In later versions it should hold all the receiving from a client and put messages into queue
            But for now this will do well
        """
        while self.isConnected:
            if not self.isAuthenticated:
                try:
                    self.logger.info("Waiting for authentication of user : " + str(self.clientId))
                    msg = Protocol.receive_string(self.sock)
                    tokens = msg.split()
                    if len(tokens) != 3:
                        self.refuse_connection()
                    if tokens[0] == "inspector":
                        self.check_authentication(tokens, PlayerType.INSPECTOR)
                    if tokens[0] == "fantom":
                        self.check_authentication(tokens, PlayerType.FANTOM)
                    if self.isAuthenticated:
                        Protocol.send_string(self.sock, "connection accepted")
                        self.logger.info(str(self.clientId) + ": Authentication accepted, Welcome !")
                        return
                    else:
                        self.refuse_connection()
                except socket.error as e:
                    if isinstance(e.args, tuple):
                        self.logger.error("errno error")
                        if e.args[0] == errno.EPIPE:
                            # remote peer disconnected
                            self.logger.error("Detected remote disconnect")
                        else:
                            # determine and handle different error
                            pass
                    else:
                        self.logger.error("socket error ", e)
                    self.disconnect()
