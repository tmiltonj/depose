import random
from enum import Enum, auto

class Card(Enum):
    LORD = auto
    BANDIT = auto
    MERCENARY = auto
    MEDIC = auto
    DIPLOMAT = auto

class Deck():
    def __init__(self):
        self.cards = []

    def add(self, card):
        self.cards.append(card)

    def get(self):
        selection = random.choice(self.cards)
        self.cards.remove(selection)
        return selection

class Player():
    def __init__(self, name):
        self.name = name
        self.coins = 0
        self.cards = []