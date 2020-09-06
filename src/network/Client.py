import errno
import time
from logging import Logger
import socket

from src.game.PlayerType import PlayerType
from src.network import Protocol
from src.utils.globals import remove_waiting_client


class Client:
    sock: socket
    isConnected: bool
    isAuthenticated: bool
    isPlaying: bool
    playerType: PlayerType
    threadId: int
    logger: Logger

    def __init__(self, sock: socket, threadId: int, logger: Logger):
        self.sock = sock
        self.threadId = threadId
        self.isConnected = True
        self.isAuthenticated = False
        self.isPlaying = False
        self.logger = logger
        self.playerType = PlayerType.UNDEFINED

    def disconnect(self):
        self.isConnected = False
        self.sock.close()
        if not self.isPlaying:
            remove_waiting_client(self)

    def handle_messages(self):
        """
            This is actually used to handle the authentication and know the type of client connecting
            In later versions it should hold all the receiving from a client and put messages into queue
            But for now this will do well
        """
        while self.isConnected:
            if self.isAuthenticated:
                time.sleep(5)
            elif not self.isAuthenticated:
                try:
                    self.logger.info("Waiting for authentication of user : " + str(self.threadId))
                    msg = Protocol.receive_string(self.sock)
                    if msg == "inspector connection":
                        self.isAuthenticated = True
                        self.playerType = PlayerType.INSPECTOR
                    if msg == "fantom connection":
                        self.isAuthenticated = True
                        self.playerType = PlayerType.FANTOM
                    if self.isAuthenticated:
                        Protocol.send_string(self.sock, "connection accepted")
                        self.logger.info(str(self.threadId) + ": Authentication accepted, Welcome !")
                    else:
                        Protocol.send_string(self.sock, "connection refused")
                        self.logger.info(str(self.threadId) + ": Authentication refused, Sorry !")
                        self.disconnect()
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
