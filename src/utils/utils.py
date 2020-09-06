import json
import sys

from src.network import Protocol
from src.utils.globals import clients, clientThreads

"""
    Functions handling exchanges between
    the players and the server.
"""


def receive_json_from_player(uuid, player):
    """
        Receives a python object from the client and converts it to a python
        object.

        :param player: object of the class Player. Either the fantom or the
        inspector.
        :return: return a python-readable object.
    """
    # logger.debug(f"receive json from player {player}")
    client = clients[uuid][player]
    received_bytes = Protocol.receive_json(client.sock)
    if len(received_bytes) == 0:
        terminate_game(clients[uuid], uuid)
    json_object = json.loads(received_bytes)
    return json_object


def send_json_to_player(uuid, player, data):
    """
        Converts a python object to json and send it to a client.

        :param player: object of the class Player. Either the fantom or the
        inspector.
        :param data: python object sent to the player.
    """
    # logger.debug(f"send json to player {player}")
    msg = json.dumps(data).encode("utf-8")
    Protocol.send_json(clients[uuid][player].sock, msg)


def ask_question_json(uuid, player, question):
    """
        Higher level function handling interaction between the server and
        the clients.

        :param player: player
        :param question: dictionary containing a type, data, and the state of
        the game.
        :return: returns the answer to the question asked.
    """
    send_json_to_player(uuid, player.id, question)
    return receive_json_from_player(uuid, player.id)


def terminate_game(game_clients, uuid):
    """
        Temporary way to handle a disconnection error during the game
        Logger is probably not closed properly tho
    """
    for client in game_clients:
        client.disconnect()
        clientThreads[client.currentThreadId].join()
        client.sock.close()

    clients.pop(uuid)
    clientThreads.pop(uuid)
    sys.exit()  # Terminate the game thread after clearing everything
