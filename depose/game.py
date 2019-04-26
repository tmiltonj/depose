from threading import Thread
from time import sleep
from depose.view import GUI, IdleState, OptionListState
from collections import deque
from depose.model import Player, Deck, Card
from depose.actions import ActionFactory, Actions

class Game():
    def __init__(self, ui, action_factory):
        self.ui = ui
        self.ui.add_observer(self)

        self.action_factory = action_factory

        self.players = []
        self.active_player = None
        self.turn_count = 1

    def add_player(self, player):
        self.players.append(player)
        # Player needs a reference to Game for user input
        player.game = self

    def wait_for_input(self, prompt, options, response):
        self.handle = response
        self.ui.set_state(
            OptionListState(
                context=self.ui,
                prompt=prompt,
                options=options
            )
        )

    def receive_action(self, action):
        print("Player chose action: ", action)
        action_map = { 
            "Salary": Actions.SALARY, 
            "Donations": Actions.DONATIONS, 
            "Tithe": Actions.TITHE,
            "Depose": Actions.DEPOSE,
            "Mug": Actions.MUG,
            "Murder": Actions.MURDER,
            "Diplomacy": Actions.DIPLOMACY,
        }

        action = self.action_factory.create(
            action_map[action], self.active_player
        )
        action.perform(game=self)
        print(action.description.format(actor=action.actor))

        #self._cleanup()

    def ask_for_counters(self, action):
        self.curr_action = action
        self.curr_ask = 0
        while self.players[self.curr_ask] == action.actor:
            self.curr_ask += 1
            if self.curr_ask >= len(self.players):
                break

        if self.curr_ask >= len(self.players):
            action._perform(self, opponent=None)
        else:
            self.players[self.curr_ask].ask_to_counter(action)

    def receive_counter(self, result):
        if result == "Yes":
            print("Received a 'YES' to counter")
            print("Currently asking ", self.players[self.curr_ask])
            self.curr_action._perform(self, opponent=self.players[self.curr_ask])
        else:
            self.curr_ask += 1
            if self.curr_ask < len(self.players):
                while self.players[self.curr_ask] == self.curr_action.actor:
                    self.curr_ask += 1
                    if self.curr_ask >= len(self.players):
                        break

            if self.curr_ask >= len(self.players):
                self.curr_action._perform(self, opponent=None)
            else:
                self.players[self.curr_ask].ask_to_counter(self.curr_action)

    def ask_for_challenges(self, action):
        self.curr_action = action
        self.curr_ask = 0
        while self.players[self.curr_ask] == action.actor:
            self.curr_ask += 1
            if self.curr_ask >= len(self.players):
                break

        if self.curr_ask >= len(self.players):
            action._perform(self, opponent=None)
        else:
            self.players[self.curr_ask].ask_to_challenge(action)

    def receive_challenge(self, result):
        if result == "Yes":
            self.curr_action._perform(self, self.players[self.curr_ask])
        else:
            self.curr_ask += 1
            if self.curr_ask < len(self.players):
                while self.players[self.curr_ask] == self.curr_action.actor:
                    self.curr_ask += 1
                    if self.curr_ask >= len(self.players):
                        break

            if self.curr_ask >= len(self.players):
                self.curr_action._perform(self, opponent=None)
            else:
                self.players[self.curr_ask].ask_to_counter(self.curr_action)
    
    def resolve_challenge(self, action):
        self.curr_action = action
        action.actor.resolve_challenge(action)

    def receive_revealed_card(self, card):
        action = self.curr_action
        if not action.is_performed_by(card):
            print("Challenge succeeded, could not perform action")
            self._cleanup()
        else:
            print("Challenge failed, can perform action")
            action.challenge_succeeded(game=self)
    
    def action_completed(self, action):
        print(action.description)
        self._cleanup()

    def _cleanup(self):
        dead = [p for p in self.players if len(p.cards) == 0]
        for dead_player in dead:
            print(dead_player.name, " has no cards left, removed from queue")
            self.players.remove(dead_player)

        if len(self.players) > 1:
            self._advance_turn()
        else:
            self._game_over()

    def _advance_turn(self):
        ap_ind = self.players.index(self.active_player)
        ap_ind = (ap_ind + 1) % len(self.players)
        self.active_player = self.players[ap_ind]

        self.take_turn(self.active_player)

    def _game_over(self):
        print("Game over! ", self.players[0], " is the winner!")

    def setup_game(self):
        for p in self.players:
            p.coins = 2
            p.draw_cards(2)

    def take_turn(self, player):
        print("Select action for ", player.name)
        player.choose_action()

    def play(self):
        self.active_player = self.players[0]
        self.take_turn(self.active_player)


if __name__ == '__main__':
    af = ActionFactory()

    d = Deck()
    d.cards = [Card.BANDIT, Card.DIPLOMAT, Card.LORD, Card.MEDIC]

    p1 = Player("Ritz", deck=d)
    p2 = Player("Sharna", deck=d)
    
    ui = GUI(players=[p1, p2])
    ui.set_state(
        IdleState(context=ui, message="Waiting...")
    )

    g = Game(ui=ui, action_factory=af)
    g.add_player(p1)
    g.add_player(p2)

    #t = Thread(target=g.play)
    #t.start()
    g.setup_game()
    g.play()

    ui.mainloop()
    ui.destroy()



