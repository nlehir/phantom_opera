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
