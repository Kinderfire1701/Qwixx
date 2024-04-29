import random

class Dice:
    def __init__(self, color):
        self.color = color
        self.value = 0

    def roll(self):
        self.value = random.randint(1, 6)