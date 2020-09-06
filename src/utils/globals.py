import logging
import os
import socket
from logging.handlers import RotatingFileHandler
from threading import Thread
from typing import List, Dict
from uuid import UUID

from src.network.Client import Client

"""
    server setup
"""
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = ''
port = 12000
sock.bind((host, port))
# list that will later contain the sockets
waiting_clients: List[Client] = []
# Dico of clients to retreive them if needed, in the future this will disapear only the room server should decide
# what to do with its client list no need for a global here
clients: Dict[UUID, List[Client]] = {}
server_running: bool = True
current_thread_id = -1
clientThreads: Dict[int, Thread] = {}
roomThreads: Dict[UUID, Thread] = {}

"""
    game data
"""
# determines whether the power of the character is used before
# or after moving
permanents = {"pink"}
both = {'red', 'grey', 'blue'}
before = {'purple', 'brown'}
after = {'black', 'white'}

# reunion of sets
colors = before | permanents | after | both

# ways between rooms
passages = [{1, 4}, {0, 2}, {1, 3}, {2, 7}, {0, 5, 8},
            {4, 6}, {5, 7}, {3, 6, 9}, {4, 9}, {7, 8}]
# ways for the pink character
pink_passages = [{1, 4}, {0, 2, 5, 7}, {1, 3, 6}, {2, 7}, {0, 5, 8, 9},
                 {4, 6, 1, 8}, {5, 7, 2, 9}, {3, 6, 9, 1}, {4, 9, 5},
                 {7, 8, 4, 6}]

"""
    logging setup
    you can set the appropriate importance level of the data
    that are written to your logfiles.
"""
loggers = {}
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# logger to file
if os.path.exists("./logs/game.log"):
    os.remove("./logs/game.log")


def create_logger(uuid: UUID):
    loggers[uuid] = logging.getLogger(str(uuid))
    loggers[uuid].setLevel(logging.DEBUG)
    file_handler = RotatingFileHandler('./logs/game' + str(uuid) + '.log', 'a', 1000000, 1)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    loggers[uuid].addHandler(file_handler)
    # logger to console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    loggers[uuid].addHandler(stream_handler)
    return loggers[uuid], file_handler, stream_handler


def create_main_logger():
    logger = logging.getLogger()
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


def delete_logger(uuid: UUID):
    del loggers[uuid]
