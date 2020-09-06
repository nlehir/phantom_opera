import cProfile
import sys
import uuid
from logging import Logger, Handler
from threading import Thread
from typing import List

from src.game.Game import Game
from src.game.Player import Player
from src.network.Client import Client
from src.utils.globals import create_logger, clients

"""
    Initialize the data before launching a game
"""


class RoomServer:
    uuid: uuid.UUID
    roomClients: List[Client]
    logger: Logger
    fileHandler: Handler
    streamHandler: Handler

    def __init__(self, roomClients: List[Client]):
        self.uuid = uuid.uuid1()
        self.roomClients = roomClients
        self.logger, self.fileHandler, self.streamHandler = create_logger(self.uuid)

    def close_logger(self):
        self.logger.removeHandler(self.fileHandler)
        self.logger.removeHandler(self.streamHandler)

    def run(self):
        self.logger.info("Room opened, initializing data for the game")

        clients[self.uuid].append(self.roomClients[0])
        clients[self.uuid].append(self.roomClients[1])

        # Player 0 is always a Inspector and 1 is Fantom : order handled by matchmaking
        players = [Player(0, self.roomClients[0], self.uuid, self.logger),
                   Player(1, self.roomClients[1], self.uuid, self.logger)]
        scores = []

        # profiling
        pr = cProfile.Profile()
        pr.enable()

        self.logger.info("Starting the game : " + str(self.uuid))

        game = Game(players, self.roomClients, self.logger)
        game.start()

        # profiling
        pr.disable()
        # stats_file = open("{}.txt".format(os.path.basename(__file__)), 'w')
        stats_file = open("./logs/profiling" + str(uuid) + ".txt", 'w')
        sys.stdout = stats_file
        pr.print_stats(sort='time')
        self.close_logger()
