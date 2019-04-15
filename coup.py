from model import Card, Deck
from view import UI
from collections import deque


def main():
    ui = UI()
    coup = Game(ui)
    coup.play()


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

    def lose_life(self):
        print("Lost a life")

    def ambassador(self):
        print("Ambassadoring")

class Game():
    def __init__(self, ui):
        self.players = deque()
        self.ui = ui

    def play(self):
        num_players = self.ui.get_integer("Enter number of players: ", "Must be between 2 - 6", 2, 6)
        for i in range(num_players):
            self.players.append(Player(coins=2)) 

        while len(self.players) > 1:
            active_player = self.players[0]
            #action = active_player.choose_action()
            #action.perform()

            self.cleanup()

            self.players.append(self.players.popleft())

    def cleanup(self):
        """
        for p in self.players:
            if (len(p.cards) <= 0):
                self.players.remove(p)
        """
        self.ui.message("Remove player 0")
        self.players.popleft()


if __name__ == '__main__':
    main()