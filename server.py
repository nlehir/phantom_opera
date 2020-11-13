import signal
import sys
from logging import Logger
from threading import Thread

from src.network.Client import Client
import src.utils.globals as glob
from src.network.Matchmaking import matchmaking

"""
    The order of connexion of the sockets is important.
    inspector is player 0, it must be represented by the first socket.
    fantom is player 1, it must be representer by the second socket.
"""


def handle_connections(logger: Logger):
    glob.sock.listen(5)
    try:
        while glob.server_running:
            (clientsocket, addr) = glob.sock.accept()
            logger.info("New client has logged on !")
            glob.current_thread_id += 1
            client = Client(clientsocket, glob.current_thread_id, logger)
            glob.waiting_clients.append(client)
            clientsocket.settimeout(500)
            clientthread = Thread(target=client.handle_messages)
            clientthread.start()
            glob.clientThreads[glob.current_thread_id] = clientthread
    except OSError:
        logger.info("Closing the network")


def sigint_handler(signum, frame):
    pass


if __name__ == '__main__':

    _logger = glob.create_main_logger()
    _logger.info("Launching server ...")

    handlerThread = Thread(target=handle_connections, args=(_logger,))
    handlerThread.start()

    matchmakingThread = Thread(target=matchmaking, args=(_logger,))
    matchmakingThread.start()

    signal.signal(signal.SIGINT, sigint_handler)

    while glob.server_running:
        command = input()
        if command == "quit":
            _logger.info("Server shutdown !")
            glob.server_running = False
            glob.sock.close()

    for ctKey in glob.clientThreads:
        glob.clientThreads[ctKey].join()
    for roomKey in glob.roomThreads:
        glob.roomThreads[roomKey].join()
    handlerThread.join()
    matchmakingThread.join()

    sys.stdout = sys.__stdout__
