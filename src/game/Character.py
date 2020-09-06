from typing import Dict, Union


class Character:
    """
        Class representing the eight possible characters of the game.
    """
    color: str
    suspect: bool
    position: int
    power_activated: bool

    def __init__(self, color: str):
        self.color = color
        self.suspect = True
        self.position = 0
        self.power_activated = False

    def __repr__(self):
        if self.suspect:
            susp = "-suspect"
        else:
            susp = "-clean"
        return self.color + "-" + str(self.position) + susp

    def display(self)-> Dict[str, Union[bool, int, str]]:
        return {
            "color": self.color,
            "suspect": self.suspect,
            "position": self.position,
            "power": self.power_activated
        }
