import json
import sys
from typing import List
from uuid import UUID

from src.network import Protocol
from src.network.Client import Client
from src.utils.globals import clients, clientThreads

"""
    Functions handling exchanges between
    the players and the server.
"""


def receive_json_from_player(client: Client, uuid: UUID):
    """
        Receives a python object from the client and converts it to a python
        object.

        :param player: object of the class Player. Either the fantom or the
        inspector.
        :return: return a python-readable object.
    """
    # logger.debug(f"receive json from player {player}")
    received_bytes = Protocol.receive(client.sock)
    if len(received_bytes) == 0:
        terminate_game(clients[uuid], uuid)
    json_object = json.loads(received_bytes)
    return json_object


def receive_json_from_client(client: Client):
    """
        Receives a python object from the client and converts it to a python
        object.
    """
    received_bytes = Protocol.receive(client.sock)
    if len(received_bytes) == 0:
        client.disconnect()
        clientThreads[client.threadId].join()
        clientThreads.pop(client.threadId)
    json_object = json.loads(received_bytes)
    return json_object


def send_json_to_player(client: Client, data):
    """
        Converts a python object to json and send it to a client.

        :param player: object of the class Player. Either the fantom or the
        inspector.
        :param data: python object sent to the player.
    """
    # logger.debug(f"send json to player {player}")
    msg = json.dumps(data).encode("utf-8")
    Protocol.send(client.sock, msg)


def ask_question_json(client: Client, uuid: UUID, question):
    """
        Higher level function handling interaction between the server and
        the clients.

        :param player: player
        :param question: dictionary containing a type, data, and the state of
        the game.
        :return: returns the answer to the question asked.
    """
    send_json_to_player(client, question)
    return receive_json_from_player(client, uuid)


def terminate_game(game_clients: List[Client], uuid: UUID):
    """
        Temporary way to handle a disconnection error during the game
        Logger is probably not closed properly tho
    """
    for client in game_clients:
        client.disconnect()
        clientThreads[client.threadId].join()
        client.sock.close()
        clientThreads.pop(client.threadId)

    clients.pop(uuid)
    sys.exit()  # Terminate the game thread after clearing everything
