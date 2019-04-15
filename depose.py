from model import Card, Deck
from view import UI
from actions import *
from collections import deque

def main():
    ui = UI()
    depose = Game(ui)
    depose.play()


class Player():
    actions = {
        "Salary":       ActionFactory.salary,
        "Donations":    ActionFactory.donations,
        "Tithe":        ActionFactory.tithe,
        "Depose":       ActionFactory.depose,
        "Mug":          ActionFactory.mug,
        "Murder":       ActionFactory.murder,
        "Diplomacy":    ActionFactory.diplomacy
    }

    def __init__(self, ui, deck, name="Player", coins=0):
        self.ui = ui
        self.deck = deck
        self.name = name
        self.coins = coins
        self.cards = []

    def choose_action(self):
        action_list = self.get_action_list()
        choice = self.ui.get_choice('Select an action: ', action_list)
        return Player.actions[choice](self)

    def get_action_list(self):
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

    def lose_life(self):
        print("Lost a life")

    def diplomacy(self):
        print("Diplomacying")

    def draw_cards(self, number=1):
        for i in range(number):
            self.cards.append(self.deck.get())


class Game():
    names = ["Shinji", "Rei", "Asuka", "Misato", "Gendo", "Kaworu"]

    @staticmethod
    def new_deck():
        deck = Deck()
        for i in range(3):
            deck.add(Card("Lord"))
            deck.add(Card("Bandit"))
            deck.add(Card("Mercenary"))
            deck.add(Card("Medic"))
            deck.add(Card("Diplomat"))

        return deck

    def __init__(self, ui):
        self.players = deque()
        self.ui = ui

    def play(self):
        deck = Game.new_deck()

        num_players = self.ui.get_integer("Enter number of players: ", "Must be between 2 - 6", 2, 6)
        for i in range(num_players):
            p = Player(self.ui, deck, Game.names[i], coins=2)
            p.draw_cards(2)
            self.players.append(p)

        while len(self.players) > 1:
            active_player = self.players[0]
            self.ui.message("\n{}'s turn".format(active_player.name))
            self.ui.message(
                "Coins: {}, Cards: {}".format(active_player.coins, active_player.cards)
            )

            action = active_player.choose_action()
            action.do()

            self.ui.message("\nCleanup phase...")
            self.cleanup()

            self.ui.message("End turn")
            self.players.append(self.players.popleft())

    def cleanup(self):
        dead_players = [p for p in self.players if len(p.cards) <= 0]
        for p in dead_players:
            self.players.remove(p)

            


if __name__ == '__main__':
    main()