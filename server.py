import cProfile
import os
import sys
from threading import Thread

from src.Game import Game
from src.Player import Player
from src.globals import clients, link
import random_fantom
import random_inspector

"""
    The order of connexion of the sockets is important.
    inspector is player 0, it must be represented by the first socket.
    fantom is player 1, it must be representer by the second socket.
"""


class InitConnexion(Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        while len(clients) != 2:
            link.listen(2)
            (clientsocket, addr) = link.accept()
            clients.append(clientsocket)
            clientsocket.settimeout(500)
        game = Game(players)
        game.lancer()
        link.close()
        print('end')


if __name__ == '__main__':
    players = [Player(0), Player(1)]
    scores = []

    game = InitConnexion()
    print('start')
    game.start()
    rfantom = random_fantom.Player()
    rfantom.start()
    rinspector = random_inspector.Player()
    rinspector.start()
    rfantom.join()
    rinspector.join()
    game.join()

    # init_connexion()
    print('the game is finished')
    # profiling
    pr = cProfile.Profile()
    pr.enable()

    # profiling
    pr.disable()
    # stats_file = open("{}.txt".format(os.path.basename(__file__)), 'w')
    stats_file = open("./logs/profiling.txt", 'w')
    sys.stdout = stats_file

    sys.stdout = sys.__stdout__
