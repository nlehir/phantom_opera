import json

import protocol
from src.globals import logger, clients

"""
    Functions handling exchanges between
    the players and the server.
"""


def receive_json_from_player(player):
    """
        Receives a python object from the client and converts it to a python
        object.

        :param player: object of the class Player. Either the fantom or the
        inspector.
        :return: return a python-readable object.
    """
    # logger.debug(f"receive json from player {player}")
    received_bytes = protocol.receive_json(clients[player])
    json_object = json.loads(received_bytes)
    return json_object


def send_json_to_player(player, data):
    """
        Converts a python object to json and send it to a client.

        :param player: object of the class Player. Either the fantom or the
        inspector.
        :param data: python object sent to the player.
    """
    # logger.debug(f"send json to player {player}")
    msg = json.dumps(data).encode("utf-8")
    protocol.send_json(clients[player], msg)


def ask_question_json(player, question):
    """
        Higher level function handling interaction between the server and
        the clients.

        :param player: player
        :param question: dictionary containing a type, data, and the state of
        the game.
        :return: returns the answer to the question asked.
    """
    send_json_to_player(player.num, question)
    return receive_json_from_player(player.num)
