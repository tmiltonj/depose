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
    def __init__(self, name, deck=None, game=None, action_factory=None):
        self.name = name
        self._coins = 0
        self._cards = []

        self.deck = deck
        self.game = game
        self.action_factory = action_factory

    @property
    def coins(self):
        return self._coins

    @coins.setter
    def coins(self, value):
        self._coins = max(0, value)

    @property
    def cards(self):
        return self._cards

    def add_card(self, card):
        self._cards.append(card)

    def __str__(self):
        return "{} (Coins: {}, Cards: {})".format(self.name, self._coins, len(self._cards))

    def draw_cards(self, number=1):
        for _ in range(number):
            self._cards.append(self.deck.get())

    def return_card(self, card=None):
        if card is None:
            card = '' # Choose a card
            #self.game.wait_for_input(options=self._cards)
        
        if card not in self._cards:
            raise ValueError("cannot find {}".format(card))

        self.deck.add(card)
        self._cards.remove(card)

    def reveal_card(self, card=None):
        if card is None:
            card = '' # Choose a card
            #self.game.wait_for_input(options=self._cards)

        if card not in self._cards:
            raise ValueError("Cannot find {}".format(card))

        return card

    def lose_life(self, card=None):
        if card is None:
            card = '' # Choose a card
            #self.game.wait_for_input(options=self._cards)
        
        if card not in self._cards:
            raise ValueError("Cannot find {}".format(card))

        self._cards.remove(card)
        return card

    def choose_action(self):
        #action_list = self._get_action_list()
        #self.game.wait_for_input(action_list)
        #self.action_factory.create()
        return

    def choose_target(self, targets):
        #target = self.game.wait_for_input(targets)
        return

    def ask_to_counter(self, action):
        #choice = self.game.wait_for_input('')
        return

    def ask_to_challenge(self, action):
        #choice = self.game.wait_for_input('')
        return