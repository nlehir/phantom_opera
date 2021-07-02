import time
from logging import Logger
from threading import Thread

from src.game.PlayerType import PlayerType
import src.utils.globals as glob
from src.network.RoomServer import RoomServer


def get_mm_delay_by_queue_size():
    return 3 / (1 + len(glob.waiting_clients))


def matchmaking(logger: Logger):
    """
        Try to match 2 clients to launch a room for those clients

        Runs every 2 sec if there are more than 2 clients in the queue
        Need some improvements to make the waiting time more dynamic for huge loads
    """

    while glob.server_running:
        # Try to match every 2 seconds
        time.sleep(get_mm_delay_by_queue_size())

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
                with glob.lockWaitingClients:
                    glob.waiting_clients.remove(mc)
            room = RoomServer(matched_clients)
            roomthread = Thread(target=room.run)
            roomthread.start()
            glob.roomThreads[room.uuid] = roomthread
