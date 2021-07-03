from __future__ import annotations

import logging
import os
import threading
from logging.handlers import RotatingFileHandler
from threading import Thread
from typing import List, Dict
from uuid import UUID

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.network.Client import Client

"""
    server setup
"""
# list that will later contain the sockets
waiting_clients: List[Client] = []
lockWaitingClients = threading.Lock()

# Dico of clients to retreive them if needed, in the future this will disapear only the room server should decide
# what to do with its client list no need for a global here
clients: Dict[UUID, List[Client]] = {}
server_running: bool = True
current_thread_id: int = -1
roomThreads: Dict[UUID, Thread] = {}

"""
    game data
"""
# determines whether the power of the character is used before
# or after moving
permanents = {"pink"}
before = {"purple", "brown"}
after = {"black", "white", "red", "blue", "grey"}

# reunion of sets
colors = {"pink",
          "blue",
          "purple",
          "grey",
          "white",
          "black",
          "red",
          "brown"}

# ways between rooms
# rooms are numbered
# from right to left
# from bottom to top
# 0 ---> 9
passages = [{1, 4}, {0, 2}, {1, 3}, {2, 7}, {0, 5, 8},
            {4, 6}, {5, 7}, {3, 6, 9}, {4, 9}, {7, 8}]
# ways for the pink character
pink_passages = [{1, 4}, {0, 2, 5, 7}, {1, 3, 6}, {2, 7}, {0, 5, 8, 9},
                 {4, 6, 1, 8}, {5, 7, 2, 9}, {3, 6, 9, 1}, {4, 9, 5},
                 {7, 8, 4, 6}]

mandatory_powers = ["red", "blue", "grey"]

"""
    logging setup
    you can set the appropriate importance level of the data
    that are written to your logfiles.
"""
loggers = {}
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# logger to file
if os.path.exists("./logs/server.log"):
    os.remove("./logs/server.log")


def create_logger(uuid: UUID):
    loggers[uuid] = logging.getLogger(str(uuid))
    loggers[uuid].setLevel(logging.INFO)
    file_handler = RotatingFileHandler('./logs/game' + str(uuid) + '.log', 'a', 1000000, 1)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    loggers[uuid].addHandler(file_handler)
    # logger to console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    loggers[uuid].addHandler(stream_handler)

    return loggers[uuid], file_handler, stream_handler


def create_main_logger():
    logger = logging.getLogger("server")
    logger.setLevel(logging.DEBUG)
    file_handler = RotatingFileHandler('./logs/server.log', 'a', 1000000, 1)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    # logger to console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    return logger


def remove_waiting_client(client: Client):
    with lockWaitingClients:
        waiting_clients.remove(client)
