from functools import partial

from depose.model import Card, Deck
from depose.player import Player
from depose.actions import (
    Action, ActionFactory, ChallengableAction, CounterableAction, TargetedAction
)
from depose.main import create_deck

def main():
    g = Game()
    g.play()


class FakeGUI():
    def set_state(self, state):
        prompt = state.prompt
        options = state.options
        print(">>", prompt)
        for ind, opt in enumerate(options, 1):
            print(">>", ind, opt)

        ind = -1
        while ind <= 0 or ind > len(options):
            try:
                ind = int(input(">> Enter choice: "))
            except ValueError:
                ind = -1

        state.context.handle(options[ind - 1])


class Game():
    def __init__(self):
        gui = FakeGUI()
        af = ActionFactory()
        deck = create_deck()

        self.players = [
            Player("A", deck, af, gui),
            Player("B", deck, af, gui),
            Player("C", deck, af, gui),
            Player("D", deck, af, gui)
        ]

        for p in self.players:
            p.player_list = self.players
            p.draw_cards(2)
            p.add_action_observer(self)

        self.obs = []

        self.active_player = -1

    def play(self):
        self.active_player += 1
        if (self.active_player >= len(self.players)):
            self.active_player = 0

        print(self.players[self.active_player].name, "takes their turn...")
        self.players[self.active_player].choose_action()

    def receive_action(self, action):
        """ Perform & listen for the outcome of the action """
        action.add_observer(self)
        action.add_decorator_observer(self)
        action.perform()

    def action_success(self, action):
        print(action.name, "succeeded!\n")
        self.play()

    def action_failed(self, action):
        print(action.name, "failed :(\n")
        self.play()

    def add_observer(self, obs):
        self.obs.append(obs)

    def remove_observer(self, obs):
        if obs in self.obs:
            self.obs.remove(obs)

    def ask_for_challenges(self, action):
        """ Prepare the list of challenge queries to ask players """
        self.questions = iter(
            [partial(Player.ask_to_challenge, p, action) 
                for p in self.players if p is not action.actor]
        )
        self.receive_decline()

    def ask_for_counters(self, action):
        """ Prepare the list of counter queries to ask players """
        if action.target is not None:
            # Only the target can block targeted actions
            action.target.ask_to_counter(action)
        else:
            self.questions = iter(
                [partial(Player.ask_to_counter, p, action) 
                    for p in self.players if p is not action.actor]
            )
            self.receive_decline()

    def receive_decline(self, source=None):
        """ Ask the next player in the challenge / counter query list

            This will notify observers if the end of the list has been reached
            source -- the Player who sent the event """
        try:
            next(self.questions)()
        except StopIteration:
            print("GAME: No more players to ask")
            for o in self.obs:
                o.notify_decline()

    def receive_accept(self, source):
        """ Notify observers if the challenge / counter was accepted """
        for o in self.obs:
            o.notify_accept(source)

    def resolve_challenge(self, action, challenger):
        """ Prompt action's actor to reveal a card """
        self.challenger = challenger
        self.action = action
        action.actor.resolve_challenge(action)

    def receive_challenge_card(self, actor, card):
        """ Resolve challenge with chosen card, notifying observers of the result """
        if self.can_perform(card, self.action):
            print(self.challenger.name, "was wrong and lost a life!")
            for o in self.obs:
                o.challenge_failed()
        else:
            print(actor.name, "cannot perform", self.action.name, "and loses a life!")
            for o in self.obs:
                o.challenge_success()

    def can_perform(self, card, action):
        """ Test if card can perform a given action """
        #TODO: Implement properly
        if card == Card.LORD:
            return action.name in ["tithe", "block donations"]
        elif card == Card.MERCENARY:
            return action.name in ["mug", "block mug"]
        else:
            return False



if __name__ == '__main__':
    main()