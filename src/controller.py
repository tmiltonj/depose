from model import Card, Deck
from actions import ActionFactory
from collections import deque


class Player():
    def __init__(self, ui, deck, game, name="Player", coins=0):
        self.ui = ui
        self.deck = deck
        self.name = name
        self.coins = coins
        self.cards = []

        af = ActionFactory(self, self.ui, game)
        self.actions = {
            "Salary":       af.salary,
            "Donations":    af.donations,
            "Tithe":        af.tithe,
            "Depose":       af.depose,
            "Mug":          af.mug,
            "Murder":       af.murder,
            "Diplomacy":    af.diplomacy
        }

    def __str__(self):
        return "{} (Coins: {}, Cards: {})".format(self.name, self.coins, len(self.cards))

    def choose_action(self):
        action_list = self._get_action_list()
        choice = self.ui.get_choice('Select an action: ', action_list)
        return self.actions[choice]()

    def called_out(self, action):
        revealed = self.ui.get_choice(
            "Your {} was called out, reveal a card: ".format(action.name),
            self.cards
        )

        if action.is_performed_by(revealed):
            self.cards.remove(revealed)
            self.deck.add(revealed)
            self.cards.append(self.deck.get())
            return True
        else:
            self.lose_life(revealed)
            return False

    def _get_action_list(self):
        if self.coins >= 10:
            return ["Depose"]

        action_list = ["Salary", "Donations", "Tithe"]
        if self.coins >= 7:
            action_list.append("Depose")

        action_list.append("Mug")

        if self.coins >= 3:
            action_list.append("Murder")
        
        action_list.append("Diplomacy")

        return action_list

    def lose_life(self, card=None):
        if card is None:
            card = self.ui.get_choice("You lost a life, reveal a card: ", self.cards)
        
        self.ui.message("{} revealed {}".format(self.name, card))
        self.cards.remove(card)

        return card

    def diplomacy(self):
        self.ui.message("{} does some Diplomacy".format(self.name))
        self.draw_cards(2)
        choice_a = self.ui.get_choice('Return 1st card to the deck', self.cards)
        self.cards.remove(choice_a)
        choice_b = self.ui.get_choice('Return 2nd card to the deck', self.cards)
        self.cards.remove(choice_b)

        self.deck.add(choice_a)
        self.deck.add(choice_b)

    def draw_cards(self, number=1):
        for i in range(number):
            self.cards.append(self.deck.get())