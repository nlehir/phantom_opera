import json
from random import randint, choice
from logging import Logger
from uuid import UUID

from src.network.Client import Client
from src.utils.globals import passages, colors, pink_passages, before, after, mandatory_powers
from src.utils.utils import ask_question_json


class Player:
    """
        Class representing the players, either the inspector (player 0)
        or the fantom (player 1)
    """
    id: int
    client: Client
    uuid: UUID

    def __init__(self, n: int, client: Client, uuid: UUID, logger: Logger):
        self.id = n
        self.client = client
        self.logger = logger
        self.uuid = uuid

        # Todo: Should not be a str, enum instead.
        self.role: str = "inspector" if n == 0 else "fantom"

    def play(self, game):
        self.logger.info("--\n" + self.role + " plays\n--")

        self.logger.debug(json.dumps(game.update_game_state(""), indent=4))
        charact = self.select(
            game.active_cards, game.update_game_state(self.role))

        # purple and brown power choose to activate or not before moving
        moved_character = self.activate_power(charact,
                                              game,
                                              before,
                                              game.update_game_state(self.role))

        self.move(charact,
                  moved_character,
                  game.blocked,
                  game.update_game_state(self.role),
                  game)

        self.activate_power(charact,
                            game,
                            after,
                            game.update_game_state(self.role))

    def select(self, active_cards, game_state):
        """
            Choose the character to activate whithin
            the given choices.
        """
        available_characters = [character.display()
                                for character in active_cards]
        question = {"question type": "select character",
                    "data": available_characters,
                    "game state": game_state}
        selected_character = ask_question_json(self.client, self.uuid, question)

        if selected_character not in range(len(active_cards)):
            warning_message = (
                ' !  : selected character not in '
                'available characters. Choosing random character.'
            )
            self.logger.warning(warning_message)
            selected_character = randint(0, len(active_cards) - 1)

        perso = active_cards[selected_character]

        # log
        self.logger.info(f"question : {question['question type']}")
        self.logger.info(f"answer : {perso}")

        del active_cards[selected_character]
        return perso

    def get_adjacent_positions(self, charact, game):
        if charact.color == "pink":
            active_passages = pink_passages
        else:
            active_passages = passages
        return [room for room in active_passages[charact.position] if set([room, charact.position]) != set(game.blocked)]

    def get_adjacent_positions_from_position(self, position, charact, game):
        if charact.color == "pink":
            active_passages = pink_passages
        else:
            active_passages = passages
        return [room for room in active_passages[position] if set([room, position]) != set(game.blocked)]

    def activate_power(self, charact, game, activables, game_state):
        """
            Use the special power of the character.
        """
        # check if the power should be used before of after moving
        # this depends on the "activables" variable, which is a set.
        if not charact.power_activated and charact.color in activables:
            # check if special power is mandatory
            if charact.color in mandatory_powers:
                power_activation = 1
            # special power is not mandatory
            else:
                question = {"question type": f"activate {charact.color} power",
                            "data": [0, 1],
                            "game state": game_state}
                power_activation = ask_question_json(self.client, self.uuid, question)

                # log
                self.logger.info(f"question : {question['question type']}")
                if power_activation == 1:
                    power_answer = "yes"
                else:
                    power_answer = "no"
                self.logger.info(f"answer  : {power_answer}")

            # the power will be used
            # charact.power represents the fact that
            # the power is still available
            if power_activation:
                self.logger.info(charact.color + " power activated")
                charact.power_activated = True

                # red character
                if charact.color == "red":
                    draw = choice(game.alibi_cards)
                    game.alibi_cards.remove(draw)
                    self.logger.info(str(draw) + " was drawn")
                    if draw == "fantom":
                        game.position_carlotta += -1 if self.id == 0 else 1
                    elif self.id == 0:
                        draw.suspect = False

                # black character
                if charact.color == "black":
                    for q in game.characters:
                        if q.position in self.get_adjacent_positions(charact, game):
                            q.position = charact.position
                            self.logger.info("new position : " + str(q))

                # white character
                if charact.color == "white":
                    for moved_character in game.characters:
                        if moved_character.position == charact.position and charact != moved_character:
                            available_positions = self.get_adjacent_positions(
                                charact, game)

                            # format the name of the moved character to string
                            character_to_move = str(
                                moved_character).split("-")[0]
                            question = {"question type": "white character power move " + character_to_move,
                                        "data": available_positions,
                                        "game state": game_state}
                            selected_index = ask_question_json(self.client, self.uuid, question)

                            # test
                            if selected_index not in range(len(available_positions)):
                                warning_message = (
                                    ' !  : selected position not available '
                                    'Choosing random position.'
                                )
                                self.logger.warning(warning_message)
                                selected_position = choice(available_positions)

                            else:
                                selected_position = available_positions[selected_index]

                            self.logger.info(
                                f"question : {question['question type']}")
                            self.logger.info("answer : " +
                                             str(selected_position))
                            moved_character.position = selected_position
                            self.logger.info("new position : " +
                                             str(moved_character))

                # purple character
                if charact.color == "purple":
                    # logger.debug("Rappel des positions :\n" + str(game))

                    available_characters = [q for q in game.characters if
                                            q.color != "purple"]
                    # the socket can not take an object
                    available_colors = [q.color for q in available_characters]

                    question = {"question type": "purple character power",
                                "data": available_colors,
                                "game state": game_state}
                    selected_index = ask_question_json(self.client, self.uuid, question)

                    # test
                    if selected_index not in range(len(colors)):
                        warning_message = (
                            ' !  : selected character not available '
                            'Choosing random character.'
                        )
                        self.logger.warning(warning_message)
                        selected_character = choice(colors)

                    else:
                        selected_character = available_characters[selected_index]

                    self.logger.info(f"question : {question['question type']}")
                    self.logger.info(f"answer : {selected_character}")

                    # swap positions
                    charact.position, selected_character.position = selected_character.position, charact.position
                    self.logger.info(f"new position : {charact}")
                    self.logger.info(f"new position : {selected_character}")

                    return selected_character

                # brown character
                if charact.color == "brown":
                    # the brown character can take one other character with him
                    # when moving.
                    available_characters = [q for q in game.characters if
                                            charact.position == q.position if
                                            q.color != "brown"]

                    # the socket can not take an object
                    available_colors = [q.color for q in available_characters]
                    if len(available_colors) > 0:
                        question = {"question type": "brown character power",
                                    "data": available_colors,
                                    "game state": game_state}
                        selected_index = ask_question_json(self.client, self.uuid, question)

                        # test
                        if selected_index not in range(len(colors)):
                            warning_message = (
                                ' !  : selected character not available '
                                'Choosing random character.'
                            )
                            self.logger.warning(warning_message)
                            selected_character = choice(colors)
                        else:
                            selected_character = available_characters[selected_index]

                        self.logger.info(f"question : {question['question type']}")
                        self.logger.info(f"answer : {selected_character}")
                        return selected_character
                    else:
                        return None

                # grey character
                if charact.color == "grey":

                    available_rooms = [room for room in range(10) if room is
                                       not game.shadow]
                    question = {"question type": "grey character power",
                                "data": available_rooms,
                                "game state": game_state}
                    selected_index = ask_question_json(self.client, self.uuid, question)

                    # test
                    if selected_index not in range(len(available_rooms)):
                        warning_message = (
                            ' !  : selected room not available '
                            'Choosing random room.'
                        )
                        self.logger.warning(warning_message)
                        selected_index = randint(
                            0, len(available_rooms) - 1)
                        selected_room = available_rooms[selected_index]

                    else:
                        selected_room = available_rooms[selected_index]

                    game.shadow = selected_room
                    self.logger.info(f"question : {question['question type']}")
                    self.logger.info("answer : " + str(game.shadow))

                # blue character
                if charact.color == "blue":

                    # choose room
                    available_rooms = [room for room in range(10)]
                    question = {"question type": "blue character power room",
                                "data": available_rooms,
                                "game state": game_state}
                    selected_index = ask_question_json(self.client, self.uuid, question)

                    # test
                    if selected_index not in range(len(available_rooms)):
                        warning_message = (
                            ' !  : selected room not available '
                            'Choosing random room.'
                        )
                        self.logger.warning(warning_message)
                        selected_index = randint(
                            0, len(available_rooms) - 1)
                        selected_room = available_rooms[selected_index]

                    else:
                        selected_room = available_rooms[selected_index]

                    # choose exit
                    passages_work = passages[selected_room].copy()
                    available_exits = list(passages_work)
                    question = {"question type": "blue character power exit",
                                "data": available_exits,
                                "game state": game_state}
                    selected_index = ask_question_json(self.client, self.uuid, question)

                    # test
                    if selected_index not in range(len(available_exits)):
                        warning_message = (
                            ' !  : selected exit not available '
                            'Choosing random exit.'
                        )
                        self.logger.warning(warning_message)
                        selected_exit = choice(passages_work)

                    else:
                        selected_exit = available_exits[selected_index]

                    self.logger.info(f"question : {question['question type']}")
                    self.logger.info("answer : " +
                                     str({selected_room, selected_exit}))
                    game.blocked = tuple((selected_room, selected_exit))
        else:
            # if the power was not used
            return None

    def move(self, charact, moved_character, blocked, game_state, game):
        """
            Select a new position for the character.
        """

        # get the number of characters in the same room
        characters_in_room = [
            q for q in game.characters if q.position == charact.position]
        number_of_characters_in_room = len(characters_in_room)
        # print(f"characters in room {characters_in_room}")
        # print(f"number of characters in room: {number_of_characters_in_room}")

        # get the available rooms from a given position
        available_rooms = list()
        available_rooms.append(self.get_adjacent_positions(charact, game))
        for step in range(1, number_of_characters_in_room):
            # build rooms that are a distance equal to step+1
            next_rooms = list()
            for room in available_rooms[step-1]:
                next_rooms += self.get_adjacent_positions_from_position(room,
                                                                        charact,
                                                                        game)
            available_rooms.append(next_rooms)

        # flatten the obtained list
        temp = list()
        for sublist in available_rooms:
            for room in sublist:
                temp.append(room)

        # filter the list in order to keep an unique occurrence of each room
        temp = set(temp)
        available_positions = list(temp)

        # test
        # print(available_positions)
        # print(game.blocked)

        # if the character is purple and the power has
        # already been used, we pass since it was already moved
        # (the positions were swapped)
        if charact.color == "purple" and charact.power_activated:
            pass

        else:
            question = {"question type": "select position",
                        "data": available_positions,
                        "game state": game_state}
            selected_index = ask_question_json(self.client, self.uuid, question)

            # test
            if selected_index not in range(len(available_positions)):
                warning_message = (
                    ' !  : selected position not available '
                    'Choosing random position.'
                )
                self.logger.warning(warning_message)
                selected_position = choice(available_positions)

            else:
                selected_position = available_positions[selected_index]

            self.logger.info(f"question : {question['question type']}")
            self.logger.info(f"answer : {selected_position}")
            self.logger.info(f"new position : {selected_position}")

            # it the character is brown and the power has been activated
            # we move several characters with him
            if charact.color == "brown" and charact.power_activated:
                charact.position = selected_position
                if moved_character:
                    moved_character.position = selected_position
            else:
                charact.position = selected_position
