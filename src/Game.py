import json
from random import shuffle, randrange
from typing import List, Set, Union

from src.Character import Character
from src.Player import Player
from src.globals import logger, passages, colors


class Game:
    """
        Class representing a full game until either the inspector
        of the fantom wins.
    """
    players: List[Player]
    position_carlotta: int
    exit: int
    num_tour: int
    shadow: int
    blocked: Set[int]
    blocked_list: List[Set[int]]
    characters: Set[Character]
    tiles: List[Character]
    active_tiles: List[Character]
    cards: List[Union[Character, str]]
    fantom: Character

    # Todo: def __init__ should be __init__(self, player_1: Player, player_2:
    #  Player)
    def __init__(self, players: List[Player]):
        # Todo: Should be self.players: Tuple[Player] = (player_1, player_2)
        self.players = players
        self.position_carlotta = 4  # position on the exit path
        # Todo: Should be removed and make the game ends when carlotta reach 0.
        self.exit = 22
        self.num_tour = 1
        # Todo: Shadow should always be placed on Joseph Buquet at the
        #  beginning of a game.
        self.shadow = randrange(10)
        # Todo: Lock should always block the hallway between the room
        #  occupied by the blue character pawn Madame Giry and the adjacent
        #  room clockwise.
        x: int = randrange(10)
        # Todo: Should be a Tuple[int]
        self.blocked = {x, passages[x].copy().pop()}
        # Todo: Unused variable, should be removed
        self.blocked_list = list(self.blocked)
        # Todo: Should be a Dict[enum, Character]
        self.characters = set({Character(color) for color in colors})
        # tiles are used to draw 4 characters at the beginning
        # of each round
        # tile means 'tuile'
        # Todo: 1 Should be rename character_cards
        self.tiles = list(self.characters)
        # Todo: Should be rename active_cards
        self.active_tiles = list()
        # Todo: Should be rename alibi_cards, declared as a List[Character]
        #  and instanciated with self.tiles.copy()
        self.cards = self.tiles[:]
        # Todo: 2 Should use random.choice() and simplified as
        #  self.fantom = random.choice(self.cards)
        self.fantom = self.cards[randrange(8)]
        # Todo: Should be placed in a logger section of the __init__()
        logger.info("the fantom is " + self.fantom.color)
        self.cards.remove(self.fantom)
        # Todo: Should be replaced by self.cards.extend(['fantom'] * 3)
        self.cards += ["fantom"] * 3

        # log
        logger.info("\n=======\nnew game\n=======")
        # Todo: 1 Should be removed
        logger.info(f"shuffle {len(self.tiles)} tiles")
        # Todo: 2 Should be removed
        logger.info(f"shuffle {len(self.cards)} cards")
        # work
        # Todo: 1 Should be removed
        shuffle(self.tiles)
        # Todo: 2 Should be removed
        shuffle(self.cards)
        # Todo:
        #   rooms_number = list(range(10))
        #   start_rooms = rooms_number[:5] + rooms_number[7:]
        #   for c in self.characters:
        #       c.position = random.choice(start_rooms)
        #       start_rooms.remove(c.position)
        for i, p in enumerate(self.tiles):
            p.position = i

        self.characters_display = [character.display() for character in
                                   self.characters]
        # Todo: should be removed
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
            # Todo: should be removed
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
        for i in [first_player_in_phase, 1 - first_player_in_phase,
                  1 - first_player_in_phase, first_player_in_phase]:
            self.players[i].play(self)

    def fantom_scream(self):
        partition: List[Set[Character]] = [
            {p for p in self.characters if p.position == i} for i in range(10)]
        if len(partition[self.fantom.position]) == 1 \
                or self.fantom.position == self.shadow:
            logger.info("The fantom screams.")
            self.position_carlotta += 1
            for room, chars in enumerate(partition):
                if len(chars) > 1 and room != self.shadow:
                    for p in chars:
                        p.suspect = False
        else:
            logger.info("the fantom does not scream.")
            for room, chars in enumerate(partition):
                if len(chars) == 1 or room == self.shadow:
                    for p in chars:
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
        self.fantom_scream()
        for p in self.characters:
            p.power = True
        self.num_tour += 1

    def lancer(self):
        """
            Run a game until either the fantom is discovered,
            or the singer leaves the opera.
        """
        # work
        while self.position_carlotta < self.exit and len(
                [p for p in self.characters if p.suspect]) > 1:
            self.tour()
        # game ends
        if self.position_carlotta < self.exit:
            logger.info(
                "----------\n---- inspector wins : fantom is " + str(
                    self.fantom))
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
        message = f"Tour: {self.num_tour},\n" \
            f"Position Carlotta / exit: {self.position_carlotta}/{self.exit},\n" \
            f"Shadow: {self.shadow},\n" \
            f"blocked: {self.blocked}".join(
            ["\n" + str(p) for p in self.characters])
        return message

    def update_game_state(self, player_role):
        """
            representation of the global state of the game.
        """
        self.characters_display = [character.display() for character in
                                   self.characters]
        # Todo: should be removed
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
            # Todo: should be removed
            "tiles": self.tiles_display,
            "active tiles": self.active_tiles_display
        }

        if player_role == "fantom":
            self.game_state["fantom"] = self.fantom.color

        return self.game_state
