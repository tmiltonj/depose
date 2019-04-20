from src.model import Card, Deck
from src.view import UI
from src.actions import ActionFactory
from collections import deque

def main():
    ui = UI()
    depose = Game(ui)
    depose.play()


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
            p = Player(self.ui, deck, self, name=Game.names[i], coins=2)
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