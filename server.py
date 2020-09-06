import cProfile
import sys
from logging import Logger
from threading import Thread

from src.game.PlayerType import PlayerType
from src.network.Client import Client
import src.utils.globals as glob
from src.network.RoomServer import RoomServer

"""
    The order of connexion of the sockets is important.
    inspector is player 0, it must be represented by the first socket.
    fantom is player 1, it must be representer by the second socket.
"""


def matchmaking(logger: Logger):
    """
        Try to match 2 clients to launch a room for those clients
    """

    matched_clients = []
    # Search for an Inspector
    for c in glob.waiting_clients:
        if c.playerType == PlayerType.INSPECTOR:
            matched_clients.append(c)
            break
    for c in glob.waiting_clients:
        if c.playerType == PlayerType.FANTOM:
            matched_clients.append(c)
            break
    if len(matched_clients) == 2:
        logger.info("Mathcmaking found a match, creating the room")
        for mc in matched_clients:
            glob.waiting_clients.remove(mc)
        room = RoomServer(matched_clients)
        roomthread = Thread(target=room.run)
        roomthread.start()
        glob.roomThreads[room.uuid] = roomthread


def run(logger: Logger):
    glob.sock.listen(5)
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
        matchmaking(logger)


if __name__ == '__main__':

    _logger = glob.create_main_logger()
    _logger.info("Launching server ...")

    run(_logger)

    for ctKey in glob.clientThreads:
        glob.clientThreads[ctKey].join()
    for roomKey in glob.roomThreads:
        glob.roomThreads[roomKey].join()

    glob.sock.close()

    sys.stdout = sys.__stdout__
