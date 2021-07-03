import signal
import sys
from logging import Logger
import socket
from threading import Thread
from time import sleep
import os

from src.network.Client import Client
import src.utils.globals as glob
from src.network.Matchmaking import matchmaking
from src.utils.csv_manager import csv_stats_file, auto_flush_file

"""
    This is the main file of the game server
"""


def handle_connections(connectionSock: socket, logger: Logger):

    connectionSock.listen(5)
    try:
        while glob.server_running:
            sleep(0.02)
            (clientsocket, addr) = connectionSock.accept()
            logger.info("New client has logged on !")
            glob.current_thread_id += 1
            clientsocket.settimeout(10)
            client = Client(clientsocket, glob.current_thread_id, logger)
            with glob.lockWaitingClients:
                glob.waiting_clients.append(client)
    except OSError:
        logger.info("Closing the network")


def sigint_handler(signum, frame):
    pass


if __name__ == '__main__':
    sock: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    host: str = ''
    port = int(os.environ.get("PORT", 12000))
    sock.bind((host, port))

    _logger = glob.create_main_logger()
    _logger.info("Launching server ...")

    handlerThread = Thread(target=handle_connections, args=(sock, _logger,))
    handlerThread.start()

    matchmakingThread = Thread(target=matchmaking, args=(_logger,))
    matchmakingThread.start()

    statFileThread = Thread(target=auto_flush_file, args=(csv_stats_file,))
    statFileThread.start()

    signal.signal(signal.SIGINT, sigint_handler)

    _logger.info("Server successfully started !")

    while glob.server_running:
        command = input()
        if command == "quit":
            _logger.info("Server shutdown !")
            glob.server_running = False
            sock.close()

    for roomKey in glob.roomThreads:
        glob.roomThreads[roomKey].join()
    handlerThread.join()
    matchmakingThread.join()
    statFileThread.join()

    csv_stats_file.close()

    sys.stdout = sys.__stdout__
