import json
import random
from typing import Tuple

from src.globals import passages, colors, pink_passages, before, both, after, logger
from src.utils import ask_question_json


class Player:
    """
        Class representing the players, either the inspector (player 0)
        or the fantom (player 1)
    """
    num: int

    def __init__(self, n: int):
        self.num = n
        # Todo: Should not be a str, enum instead.
        self.role: str = "inspector" if n == 0 else "fantom"

    def play(self, game):
        logger.info("--\n" + self.role + " plays\n--")

        logger.debug(json.dumps(game.update_game_state(""), indent=4))
        charact = self.select(game.active_cards,
                              game.update_game_state(self.role))

        # red character can choose to activate its power
        # before OR after moving
        if charact.color == "red":
            activation_possibilities = ["before", "after"]
            question = {"question type": "red character power activation time",
                        "data": activation_possibilities,
                        "game state": game.update_game_state(self.role)}

            power_activation_time = ask_question_json(self, question)
            if power_activation_time not in [0, 1]:
                power_activation_time = random.choice(activation_possibilities)
            else:
                power_activation_time = activation_possibilities[power_activation_time]

            # now play red character
            if power_activation_time=="before":
                moved_characters = self.activate_power(charact,
                                                       game,
                                                       before | both,
                                                       game.update_game_state(self.role))

                self.move(charact,
                          [charact],
                          game.blocked,
                          game.update_game_state(self.role))
            else:
                self.move(charact,
                          [charact],
                          game.blocked,
                          game.update_game_state(self.role))

                self.activate_power(charact,
                                    game,
                                    after | both,
                                    game.update_game_state(self.role))


        # character is not red
        else:
            moved_characters = self.activate_power(charact,
                                                   game,
                                                   before | both,
                                                   game.update_game_state(self.role))

            self.move(charact,
                      moved_characters,
                      game.blocked,
                      game.update_game_state(self.role))

            self.activate_power(charact,
                                game,
                                after | both,
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
            selected_character = random.randint(0, len(t) - 1)

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
                    draw = random.choice(game.alibi_cards)
                    game.alibi_cards.remove(draw)
                    logger.info(str(draw) + " was drawn")
                    if draw == "fantom":
                        game.position_carlotta += -1 if self.num == 0 else 1
                    elif self.num == 0:
                        draw.suspect = False

                # black character
                if charact.color == "black":
                    for q in game.characters:
                        if q.position in {x for x in passages[charact.position] if
                                          x not in game.blocked or q.position not in game.blocked}:
                            q.position = charact.position
                            logger.info("new position : " + str(q))

                # white character
                if charact.color == "white":
                    for moved_character in game.characters:
                        if moved_character.position == charact.position and charact != moved_character:
                            disp = {
                                x for x in passages[charact.position]
                                if x not in game.blocked or moved_character.position not in game.blocked}

                            # edit
                            available_positions = list(disp)
                            # format the name of the moved character to string
                            character_to_move = str(
                                moved_character).split("-")[0]
                            question = {"question type": "white character power move " + character_to_move,
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
                            logger.info("new position : " +
                                        str(moved_character))

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
                    logger.info("answer : " + selected_character)

                    # y a pas plus simple ?
                    selected_crctr = [x for x in game.characters if x.color
                                      == selected_character][0]
                    charact.position, selected_crctr.position = selected_crctr.position, charact.position
                    logger.info("new position : " + str(charact))
                    logger.info("new position : " + str(selected_crctr))

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
                            0, len(available_rooms) - 1)
                        selected_room = available_rooms[selected_index]

                    else:
                        selected_room = available_rooms[selected_index]

                    game.shadow = selected_room
                    logger.info(f"question : {question['question type']}")
                    logger.info("answer : " + str(game.shadow))

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
                    game.blocked = tuple((selected_room, selected_exit))
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
            logger.info("answer : " + str(selected_position))

            if len(moved_characters) > 1:
                logger.debug("more than one character moves")
            for q in moved_characters:
                q.position = selected_position
                logger.info("new position : " + str(q))
