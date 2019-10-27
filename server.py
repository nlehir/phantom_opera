from random import shuffle, randrange
import cProfile
import sys
import random
import os
import logging
from logging.handlers import RotatingFileHandler
import json
import socket
import protocol

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
permanents, two, before, after = {'pink'}, {
    'red', 'grey', 'blue'}, {'purple', 'brown'}, {'black', 'white'}
# reunion of sets
colors = before | permanents | after | two
# ways between rooms
passages = [{1, 4}, {0, 2}, {1, 3}, {2, 7}, {0, 5, 8},
            {4, 6}, {5, 7}, {3, 6, 9}, {4, 9}, {7, 8}]
# ways for the pink character
pink_passages = [{1, 4}, {0, 2, 5, 7}, {1, 3, 6}, {2, 7}, {0, 5, 8, 9}, {
    4, 6, 1, 8}, {5, 7, 2, 9}, {3, 6, 9, 1}, {4, 9, 5}, {7, 8, 4, 6}]


"""
    logging setup
    you can set the appropriate importance level of the data
    that are written to your logfiles.
"""
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# logger to file
if os.path.exists("./logs/game.log"):
    os.remove("./logs/game.log")
file_handler = RotatingFileHandler('./logs/game.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# logger to console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


"""
    Functions handling exchanges between
    the players and the server.
"""


def send_json_to_player(player, data):
    """
        Converts a python object to json and send it to a client.

        :param player: object of the class Player. Either the fantom or the
        inspector.
        :param data: python object sent to the player.
    """
    logger.debug(f"send json to player {player}")
    msg = json.dumps(data).encode("utf-8")
    protocol.send_json(clients[player], msg)


def receive_json_from_player(player):
    """
        Receives a python object from the client and converts it to a python
        object.

        :param player: object of the class Player. Either the fantom or the
        inspector.
        :return: return a python-readable object.
    """
    logger.debug(f"receive json from player {player}")
    received_bytes = protocol.receive_json(clients[player])
    json_object = json.loads(received_bytes)
    return json_object


def ask_question_json(player, question):
    """
        Higher level function handling interaction between the server and
        the clients.

        :param player: player
        :param questin: dictionary containing a type, data, and the state of
        the game.
        :return: returns the answer to the question asked.
    """
    send_json_to_player(player.numero, question)
    return receive_json_from_player(player.numero)


"""
    game
"""


class Character:
    """
        Class representing the eight possible characters of the game.
    """

    def __init__(self, color):
        self.color, self.suspect, self.position, self.power = color, True, 0, True

    def __repr__(self):
        if self.suspect:
            susp = "-suspect"
        else:
            susp = "-clean"
        return self.color + "-" + str(self.position) + susp

    def display(self):
        return {
            "color": self.color,
            "suspect": self.suspect,
            "position": self.position,
            "power": self.power
        }


class Player:
    """
        Class representing the players, either the inspector (player 0)
        or the fantom (player 1)
    """

    def __init__(self, n):
        self.numero = n
        self.role = "inspector" if n == 0 else "fantom"

    def play(self, game):
        logger.info("--\n"+self.role+" plays\n--")

        logger.debug(json.dumps(game.update_game_state(""), indent=4))
        charact = self.select(game.active_tiles,
                              game.update_game_state(self.role))

        moved_characters = self.activate_power(charact,
                                               game,
                                               before | two,
                                               game.update_game_state(self.role))

        self.move(charact,
                  moved_characters,
                  game.blocked,
                  game.update_game_state(self.role))

        self.activate_power(charact,
                            game,
                            after | two,
                            game.update_game_state(self.role))

    def select(self, t, game_state):
        """
            Choose the character to activate whithin
            the given choices.
        """
        available_characters = [character.display() for character in t]
        question = {"question type": "select character",
                    "data": available_characters,
                    "game state": game_state}
        selected_character = ask_question_json(self, question)

        # test
        # range(len(t)) goes until len(t)-1
        if selected_character not in range(len(t)):
            warning_message = (
                ' !  : selected character not in '
                'available characters. Choosing random character.'
            )
            logger.warning(warning_message)
            selected_character = random.randint(0, len(t)-1)

        perso = t[selected_character]

        # log
        logger.info(f"question : {question['question type']}")
        logger.info(f"answer : {perso}")

        del t[selected_character]
        return perso

    def activate_power(self, charact, game, activables, game_state):
        """
            Use the special power of the character.
        """
        # check if the power should be used before of after moving
        # this depends on the "activables" variable, which is a set.
        if charact.power and charact.color in activables:
            character_color = charact.display()["color"]
            question = {"question type": f"activate {character_color} power",
                        "data": [0, 1],
                        "game state": game_state}
            power_activation = ask_question_json(self, question)

            # log
            logger.info(f"question : {question['question type']}")
            if power_activation == 1:
                power_answer = "yes"
            else:
                power_answer = "no"
            logger.info("answer  : " + power_answer)

            # work
            if power_activation:
                logger.info(charact.color + " power activated")
                charact.power = False

                # red character
                if charact.color == "red":
                    draw = game.cards[0]
                    logger.info(str(draw) + " was drawn")
                    if draw == "fantom":
                        game.position_carlotta += -1 if self.numero == 0 else 1
                    elif self.numero == 0:
                        draw.suspect = False
                    del game.cards[0]

                # black character
                if charact.color == "black":
                    for q in game.characters:
                        if q.position in {x for x in passages[charact.position] if x not in game.blocked or q.position not in game.blocked}:
                            q.position = charact.position
                            logger.info("new position : "+str(q))

                # white character
                if charact.color == "white":
                    for moved_character in game.characters:
                        if moved_character.position == charact.position and charact != moved_character:
                            disp = {
                                x for x in passages[charact.position] if x not
                                in game.blocked or moved_character.position not in game.blocked}

                            # edit
                            available_positions = list(disp)
                            # format the name of the moved character to string
                            character_to_move = str(
                                moved_character).split("-")[0]
                            question = {"question type": "white character power move "+character_to_move,
                                        "data": available_positions,
                                        "game state": game_state}
                            selected_index = ask_question_json(self, question)

                            # test
                            if selected_index not in range(len(disp)):
                                warning_message = (
                                    ' !  : selected position not available '
                                    'Choosing random position.'
                                )
                                logger.warning(warning_message)
                                selected_position = disp.pop()

                            else:
                                selected_position = available_positions[selected_index]

                            logger.info(
                                f"question : {question['question type']}")
                            logger.info("answer : " +
                                        str(selected_position))
                            moved_character.position = selected_position
                            logger.info("new position : "+str(moved_character))

                # purple character
                if charact.color == "purple":
                    # logger.debug("Rappel des positions :\n" + str(game))

                    available_characters = list(colors)
                    available_characters.remove("purple")
                    question = {"question type": "purple character power",
                                "data": available_characters,
                                "game state": game_state}
                    selected_index = ask_question_json(self, question)

                    # test
                    if selected_index not in range(len(colors)):
                        warning_message = (
                            ' !  : selected character not available '
                            'Choosing random character.'
                        )
                        logger.warning(warning_message)
                        selected_character = colors.pop()

                    else:
                        selected_character = available_characters[selected_index]

                    logger.info(f"question : {question['question type']}")
                    logger.info("answer : "+selected_character)

                    # y a pas plus simple ?
                    selected_crctr = [x for x in game.characters if x.color
                                      == selected_character][0]
                    charact.position, selected_crctr.position = selected_crctr.position, charact.position
                    logger.info("new position : "+str(charact))
                    logger.info("new position : "+str(selected_crctr))

                # brown character
                if charact.color == "brown":
                    # the brown character can take other characters with him
                    # when moving.
                    return [q for q in game.characters if charact.position == q.position]

                # grey character
                if charact.color == "grey":

                    available_rooms = [room for room in range(10)]
                    question = {"question type": "grey character power",
                                "data": available_rooms,
                                "game state": game_state}
                    selected_index = ask_question_json(self, question)

                    # test
                    if selected_index not in range(len(available_rooms)):
                        warning_message = (
                            ' !  : selected room not available '
                            'Choosing random room.'
                        )
                        logger.warning(warning_message)
                        selected_index = random.randint(
                            0, len(available_rooms)-1)
                        selected_room = available_rooms[selected_index]

                    else:
                        selected_room = available_rooms[selected_index]

                    game.shadow = selected_room
                    logger.info(f"question : {question['question type']}")
                    logger.info("answer : "+str(game.shadow))

            # blue character
                if charact.color == "blue":

                    # choose room
                    available_rooms = [room for room in range(10)]
                    question = {"question type": "blue character power room",
                                "data": available_rooms,
                                "game state": game_state}
                    selected_index = ask_question_json(self, question)

                    # test
                    if selected_index not in range(len(available_rooms)):
                        warning_message = (
                            ' !  : selected room not available '
                            'Choosing random room.'
                        )
                        logger.warning(warning_message)
                        selected_index = random.randint(
                            0, len(available_rooms)-1)
                        selected_room = available_rooms[selected_index]

                    else:
                        selected_room = available_rooms[selected_index]

                    # choose exit
                    passages_work = passages[selected_room].copy()
                    available_exits = list(passages_work)
                    question = {"question type": "blue character power exit",
                                "data": available_exits,
                                "game state": game_state}
                    selected_index = ask_question_json(self, question)

                    # test
                    if selected_index not in range(len(available_exits)):
                        warning_message = (
                            ' !  : selected exit not available '
                            'Choosing random exit.'
                        )
                        logger.warning(warning_message)
                        selected_exit = passages_work.pop()

                    else:
                        selected_exit = available_exits[selected_index]

                    logger.info(f"question : {question['question type']}")
                    logger.info("answer : " +
                                str({selected_room, selected_exit}))
                    game.blocked = {selected_room, selected_exit}
                    game.blocked_list = list(game.blocked)
        return [charact]

    def move(self, charact, moved_characters, blocked, game_state):
        """
            Select a new position for the character.
        """
        pass_act = pink_passages if charact.color == 'pink' else passages
        if charact.color != 'purple' or charact.power:
            disp = {x for x in pass_act[charact.position]
                    if charact.position not in blocked or x not in blocked}

            available_positions = list(disp)
            question = {"question type": "select position",
                        "data": available_positions,
                        "game state": game_state}
            selected_index = ask_question_json(self, question)

            # test
            if selected_index not in range(len(disp)):
                warning_message = (
                    ' !  : selected position not available '
                    'Choosing random position.'
                )
                logger.warning(warning_message)
                selected_position = disp.pop()

            else:
                selected_position = available_positions[selected_index]

            logger.info(f"question : {question['question type']}")
            logger.info("answer : "+str(selected_position))

            if len(moved_characters) > 1:
                logger.debug("more than one character moves")
            for q in moved_characters:
                q.position = selected_position
                logger.info("new position : "+str(q))


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
        self.cards += ["fantom"]*3

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
            "active tiles": self.active_tiles_display,
        }

    def actions(self):
        player_actif = self.num_tour % 2
        if player_actif == 1:
            logger.info(f"-\nshuffle {len(self.tiles)} tiles\n-")
            shuffle(self.tiles)
            self.active_tiles = self.tiles[:4]
        else:
            self.active_tiles = self.tiles[4:]
        for i in [player_actif, 1-player_actif, 1-player_actif, player_actif]:
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
            f"---- final score : {self.exit-self.position_carlotta}\n----------")
        return self.exit - self.position_carlotta

    def __repr__(self):
        message = f"Tour: {self.num_tour},\n"
        message += f"Position Carlotta / exit: {self.position_carlotta}/{self.exit},\n"
        message += f"Shadow: {self.shadow},\n"
        message += f"blocked: {self.blocked}"
        message += "".join(["\n"+str(p) for p in self.characters])
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
            "active tiles": self.active_tiles_display,
        }

        if (player_role == "fantom"):
            self.game_state["fantom"] = self.fantom.color

        return self.game_state


players = [Player(0), Player(1)]
scores = []

"""
    The order of connexion of the sockets is important.
    inspector is player 0, it must be represented by the first socket.
    fantom is player 1, it must be representer by the second socket.
"""


def init_connexion():
    while len(clients) != 2:
        link.listen(2)
        (clientsocket, addr) = link.accept()
        logger.info("Received client !")
        clients.append(clientsocket)
        clientsocket.settimeout(500)


logger.info("no client yet")
init_connexion()
logger.info("received all clients")

# profiling
pr = cProfile.Profile()
pr.enable()

game = Game(players)
game.lancer()

link.close()

# profiling
pr.disable()
# stats_file = open("{}.txt".format(os.path.basename(__file__)), 'w')
stats_file = open("./logs/profiling.txt", 'w')
sys.stdout = stats_file
pr.print_stats(sort='time')

sys.stdout = sys.__stdout__
