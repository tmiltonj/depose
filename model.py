import random

from events import *

class Card():
    def __init__(self, name):
        self.name = name

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
    def __init__(self, coins=0):
        self.coins = coins
        self.cards = []

    def choose_action(self):
        if (self.coins >= 10):
            print("More than 10 coins, must coup")
            return "Coup"
        else:
            print("Pick an action from the list")
            return "Action"


def main():
    d = Deck()
    d.add(Card("A"))
    d.add(Card("B"))
    d.add(Card("C"))

    print(d.get().name)
    print(d.get().name)
    print(d.get().name)

if __name__ == '__main__':
    main()