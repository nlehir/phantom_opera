import logging
import os
import socket
from logging.handlers import RotatingFileHandler

"""
    server setup
"""
link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
link.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = ''
port = 12000
link.bind((host, port))
# list that will later contain the sockets
clients = []

"""
    game data
"""
# determines whether the power of the character is used before
# or after moving
permanents = {'pink'}
two = {'red', 'grey', 'blue'}
before = {'purple', 'brown'}
after = {'black', 'white'}

# reunion of sets
colors = before | permanents | after | two
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
