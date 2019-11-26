import json
from random import shuffle, randrange

from src.Character import Character
from src.globals import logger, passages, colors


class Game:
    """
        Class representing a full game until either the inspector
        of the fantom wins.
    """

    def __init__(self, players):
        self.players = players
        self.position_carlotta, self.exit, self.num_tour, self.shadow, x = 4, 22, 1, randrange(
            10), randrange(10)
        self.blocked = {x, passages[x].copy().pop()}
        self.blocked_list = list(self.blocked)
        self.characters = {Character(c) for c in colors}
        # tiles are used to draw 4 characters at the beginning
        # of each round
        # tile means 'tuile'
        self.tiles = [p for p in self.characters]
        self.active_tiles = []
        # cards are for the red character
        self.cards = self.tiles[:]
        self.fantom = self.cards[randrange(8)]
        logger.info("the fantom is " + self.fantom.color)
        self.cards.remove(self.fantom)
        self.cards += ["fantom"] * 3

        # log
        logger.info("\n=======\nnew game\n=======")
        logger.info(f"shuffle {len(self.tiles)} tiles")
        logger.info(f"shuffle {len(self.cards)} cards")
        # work
        shuffle(self.tiles)
        shuffle(self.cards)
        for i, p in enumerate(self.tiles):
            p.position = i

        self.characters_display = [character.display() for character in
                                   self.characters]
        self.tiles_display = [tile.display() for tile in
                              self.tiles]
        self.active_tiles_display = [tile.display() for tile in
                                     self.active_tiles]

        self.game_state = {
            "position_carlotta": self.position_carlotta,
            "exit": self.exit,
            "num_tour": self.num_tour,
            "shadow": self.shadow,
            "blocked": self.blocked_list,
            "characters": self.characters_display,
            "tiles": self.tiles_display,
            "active tiles": self.active_tiles_display,
        }

    def actions(self):
        """
        phase = tour
        phase 1 : IFFI
        phase 2 : FIIF
        first phase : initially num_tour = 1, then 3, 5, etc.
        so the first player to play is (1+1)%2=0 (inspector)
        second phase : num_tour = 2, 4, 6, 8, etc.
        so the first player to play is (2+1)%2=1 (fantom)
        """
        first_player_in_phase = (self.num_tour + 1) % 2
        if first_player_in_phase == 0:
            logger.info(f"-\nshuffle {len(self.tiles)} tiles\n-")
            shuffle(self.tiles)
            self.active_tiles = self.tiles[:4]
        else:
            self.active_tiles = self.tiles[4:]
        for i in [first_player_in_phase, 1-first_player_in_phase, 1-first_player_in_phase, first_player_in_phase]:
            self.players[i].play(self)

    def lumiere(self):
        partition = [{p for p in self.characters if p.position == i}
                     for i in range(10)]
        if len(partition[self.fantom.position]) == 1 or self.fantom.position == self.shadow:
            logger.info("The fantom screams.")
            self.position_carlotta += 1
            for piece, gens in enumerate(partition):
                if len(gens) > 1 and piece != self.shadow:
                    for p in gens:
                        p.suspect = False
        else:
            logger.info("the fantom does not scream.")
            for piece, gens in enumerate(partition):
                if len(gens) == 1 or piece == self.shadow:
                    for p in gens:
                        p.suspect = False
        self.position_carlotta += len(
            [p for p in self.characters if p.suspect])

    def tour(self):
        # log
        logger.info("\n------------------")
        logger.info(self)
        logger.debug(json.dumps(self.update_game_state(""), indent=4))

        # work
        self.actions()
        self.lumiere()
        for p in self.characters:
            p.power = True
        self.num_tour += 1

    def lancer(self):
        """
            Run a game until either the fantom is discovered,
            or the singer leaves the opera.
        """
        # work
        while self.position_carlotta < self.exit and len([p for p in self.characters if p.suspect]) > 1:
            self.tour()
        # game ends
        if self.position_carlotta < self.exit:
            logger.info(
                "----------\n---- inspector wins : fantom is " + str(self.fantom))
        else:
            logger.info("----------\n---- fantom wins")
        # log
        logger.info(
            f"---- final position of Carlotta : {self.position_carlotta}")
        logger.info(f"---- exit : {self.exit}")
        logger.info(
            f"---- final score : {self.exit - self.position_carlotta}\n----------")
        return self.exit - self.position_carlotta

    def __repr__(self):
        message = f"Tour: {self.num_tour},\n"
        message += f"Position Carlotta / exit: {self.position_carlotta}/{self.exit},\n"
        message += f"Shadow: {self.shadow},\n"
        message += f"blocked: {self.blocked}"
        message += "".join(["\n" + str(p) for p in self.characters])
        return message

    def update_game_state(self, player_role):
        """
            representation of the global state of the game.
        """
        self.characters_display = [character.display() for character in
                                   self.characters]
        self.tiles_display = [tile.display() for tile in
                              self.tiles]
        self.active_tiles_display = [tile.display() for tile in
                                     self.active_tiles]
        # update

        self.game_state = {
            "position_carlotta": self.position_carlotta,
            "exit": self.exit,
            "num_tour": self.num_tour,
            "shadow": self.shadow,
            "blocked": self.blocked_list,
            "characters": self.characters_display,
            "tiles": self.tiles_display,
            "active tiles": self.active_tiles_display
        }

        if player_role == "fantom":
            self.game_state["fantom"] = self.fantom.color

        return self.game_state
