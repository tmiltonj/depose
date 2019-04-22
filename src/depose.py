from threading import Thread
from time import sleep

from view import GUI, IdleState, OptionListState
from model import Deck, Card, Player
#import controller

def main():
    deck = create_deck()
    players = create_players(num_players=4, deck=deck)

    gui = GUI(players=players)
    game = Game(players=players, state=StartTurnState(), ui=gui)

    gui.add_observer(game)
    game.update()

    gui.mainloop()
    gui.destroy()

def create_deck(num_sets=3):
    deck = Deck()
    for _ in range(num_sets):
        deck.add(Card.LORD)
        deck.add(Card.BANDIT)
        deck.add(Card.MERCENARY)
        deck.add(Card.MEDIC)
        deck.add(Card.DIPLOMAT)

    return deck

def create_players(num_players, game=None, deck=None, ui=None):
    import random
    names = ["Shinji", "Rei", "Asuka", "Misato", "Gendo", "Kaworu"]
    random.shuffle(names)

    players = []
    for i in range(num_players):
        p = Player(names[i])
        players.append(p)
    return players


class Game():
    def __init__(self, players, state=None, ui=None):
        self.turn_num = 0
        self.state = state
        self.ui = ui

        self.players = players
        self.active_player = 0
        self.turn_count = 1

    def set_state(self, state):
        self.state = state
        self.update()

    def update(self):
        self.ui.set_state(
            IdleState(self.ui, "Please wait...")
        )
        t = Thread(
            target = self.state.update, 
            kwargs= {"context": self}
        )
        t.start()

    def message(self, text):
        if self.ui:
            self.ui.message(text)

    def wait_for_input(self, prompt, options):
        self.ui.set_state(
            OptionListState(self.ui, prompt, options)
        )

    def handle(self, event):
        try:
            getattr(self.state, 'handle')
            self.state.handle(self, event)
        except AttributeError:
            self.message('Cannot notify current state!')

    def next_turn(self):
        self.active_player += 1
        if self.active_player >= len(self.players):
            self.turn_count += 1
            self.active_player = 0

        self.ui.player_panel.set_active(self.active_player)
        return self.active_player


class StartTurnState():
    def update(self, context):
        turn_num = context.next_turn()
        context.message("Start turn {}".format(turn_num))
        sleep(1)
        context.set_state(ChooseActionState())

class ChooseActionState():
    def update(self, context):
        context.message("Player chooses an action")
        context.wait_for_input("Choose an Action", ["Salary", "Donations", "Tithe", "Depose", "Mug", "Murder", "Diplomacy"])

    def handle(self, context, event):
        context.message("ChooseAction received " + event)
        context.set_state(PerformActionState())

class PerformActionState():
    def update(self, context):
        context.message("Performing Action!")
        sleep(1)
        context.set_state(CleanupState())

class CleanupState():
    def update(self, context):
        context.message("Cleaning up...")
        sleep(1)
        context.set_state(StartTurnState())


if __name__ == '__main__':
    main()