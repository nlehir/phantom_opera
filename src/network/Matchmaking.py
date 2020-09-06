import time
from logging import Logger
from threading import Thread

from src.game.PlayerType import PlayerType
import src.utils.globals as glob
from src.network.RoomServer import RoomServer


def matchmaking(logger: Logger):
    """
        Try to match 2 clients to launch a room for those clients
        For the moment matchmaking is triggered once for each client authenticated
        No need to run it on a dedicated thread each x minutes because disconnections while in queue
        Should be quit rare
    """

    while glob.server_running:
        # Try to match every 2 seconds
        time.sleep(2)

        if len(glob.waiting_clients) < 2:
            continue
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
