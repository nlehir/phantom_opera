import json
from random import shuffle, randrange, choice
from typing import List, Set, Union, Tuple

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
    blocked: Tuple[int]
    characters: Set[Character]
    character_cards: List[Character]
    active_cards: List[Character]
    cards: List[Union[Character, str]]
    fantom: Character

    # Todo: def __init__ should be __init__(self, player_1: Player, player_2:
    #  Player)
    def __init__(self, players: List[Player]):
        # Todo: Should be self.players: Tuple[Player] = (player_1, player_2)
        self.players = players
        self.position_carlotta = 6  # position on the exit path
        # Todo: Should be removed and make the game ends when carlotta reach 0.
        self.exit = 22
        self.num_tour = 1
        # Todo: Should be a Dict[enum, Character]
        self.characters = set({Character(color) for color in colors})
        # character_cards are used to draw 4 characters at the beginning
        # of each round
        self.character_cards = list(self.characters)
        self.active_cards = list()
        self.alibi_cards = self.character_cards.copy()
        self.fantom = choice(self.alibi_cards)
        # Todo: Should be placed in a logger section of the __init__()
        logger.info("the fantom is " + self.fantom.color)
        self.alibi_cards.remove(self.fantom)
        self.alibi_cards.extend(['fantom'] * 3)

        # log
        logger.info("\n=======\nnew game\n=======")
        # Todo: 1 Should be removed
        logger.info(f"shuffle {len(self.character_cards)} character_cards")
        # Todo: 2 Should be removed
        logger.info(f"shuffle {len(self.alibi_cards)} alibi cards")
        # work
        # Todo: 1 Should be removed
        shuffle(self.character_cards)
        # Todo: 2 Should be removed
        shuffle(self.alibi_cards)

        # Initialise character positions
        # Rooms at the center of the game are not available
        rooms_number = list(range(10))
        start_rooms = rooms_number[:5] + rooms_number[7:]
        for character in self.characters:
            character.position = choice(start_rooms)

        for character in self.characters:
            # get position of grey character
            if character.color == "grey":
                grey_character_position = character.display()["position"]
                self.shadow = grey_character_position
            if character.color == "blue":
                blue_character_position = character.display()["position"]
                # initially the blocked passage is
                # next to blue character clockwise
                if blue_character_position == 0:
                    self.blocked = (0, 1)
                elif blue_character_position == 1:
                    self.blocked = (1, 2)
                elif blue_character_position == 2:
                    self.blocked = (2, 3)
                elif blue_character_position == 3:
                    self.blocked = (3, 4)
                elif blue_character_position == 4:
                    self.blocked = (4, 5)
                elif blue_character_position == 7:
                    self.blocked = (7, 9)
                elif blue_character_position == 9:
                    self.blocked = (8, 9)
                elif blue_character_position == 8:
                    self.blocked = (4, 8)
                else:
                    print(blue_character_position)
                    raise ValueError("Wrong initial position of blue character")



        self.characters_display = [character.display() for character in
                                   self.characters]

        # Todo: should be removed
        self.character_cards_display = [tile.display() for tile in
                                        self.character_cards]
        self.active_cards_display = [tile.display() for tile in
                                     self.active_cards]

        self.game_state = {
            "position_carlotta": self.position_carlotta,
            "exit": self.exit,
            "num_tour": self.num_tour,
            "shadow": self.shadow,
            "blocked": self.blocked,
            "characters": self.characters_display,
            # Todo: should be removed
            "character_cards": self.character_cards_display,
            "active character_cards": self.active_cards_display,
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
            logger.info(
                f"-\nshuffle {len(self.character_cards)} character_cards\n-")
            shuffle(self.character_cards)
            self.active_cards = self.character_cards[:4]
        else:
            self.active_cards = self.character_cards[4:]

        # the characters should be able to use their power at each new round
        for card in self.active_cards:
            card.power_activated = False

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
        self.character_cards_display = [tile.display() for tile in
                                        self.character_cards]
        self.active_cards_display = [tile.display() for tile in
                                     self.active_cards]
        # update

        self.game_state = {
            "position_carlotta": self.position_carlotta,
            "exit": self.exit,
            "num_tour": self.num_tour,
            "shadow": self.shadow,
            "blocked": self.blocked,
            "characters": self.characters_display,
            # Todo: should be removed
            "character_cards": self.character_cards_display,
            "active character_cards": self.active_cards_display
        }

        if player_role == "fantom":
            self.game_state["fantom"] = self.fantom.color

        return self.game_state
