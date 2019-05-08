from functools import partial
from collections import deque

from depose.model import Card
from depose.player import Player


class Game():
    def __init__(self, players, ui):
        self.players = players 
        for p in self.players:
            p.add_action_observer(self)

        self.ui = ui
        self.obs = []
        self.turn_queue = deque(players)

    def play(self):
        self.active_player = self.turn_queue.popleft()

        self.ui.update_active_player(self.active_player)

        self.message("{}'s TURN".format(self.active_player.name))
        self.active_player.choose_action()

    def message(self, message):
        self.ui.message("GAME: {}".format(message))

    def receive_action(self, action):
        """ Perform & listen for the outcome of the action """
        self.message("{} chose {}\n".format(action.actor.name, action.name))
        action.add_observer(self)
        action.add_decorator_observer(self)
        action.perform()

    def action_success(self, action):
        self.message("{} succeeded!\n".format(action.name))
        action.remove_observer(self)
        action.remove_decorator_observer(self)
        self.cleanup()

    def action_failed(self, action):
        self.message("{} failed :(\n".format(action.name))
        action.remove_observer(self)
        action.remove_decorator_observer(self)
        self.cleanup()

    def cleanup(self):
        self.turn_queue.append(self.active_player)
        for p in self.players:
            if p in self.turn_queue and len(p.cards) == 0:
                self.message("{} has no more cards and was eliminated!\n".format(p.name))
                self.turn_queue.remove(p)

        self.play()

    def add_observer(self, obs):
        self.obs.append(obs)

    def remove_observer(self, obs):
        if obs in self.obs:
            self.obs.remove(obs)

    def ask_for_challenges(self, action):
        """ Prepare the list of challenge queries to ask players """
        self.message("Check if anyone challenges {}".format(action.name))
        self.questions = iter(
            [(p.name, partial(Player.ask_to_challenge, p, action)) 
                for p in self.players if p is not action.actor]
        )
        self.receive_decline()

    def ask_for_counters(self, action):
        """ Prepare the list of counter queries to ask players """
        self.message("Check if anyone counters {}".format(action.name))
        if action.target is not None:
            # Only the target can block targeted actions
            self.message("Asking {}...".format(action.target.name))
            action.target.ask_to_counter(action)
        else:
            self.questions = iter(
                [(p.name, partial(Player.ask_to_counter, p, action))
                    for p in self.players if p is not action.actor]
            )
            self.receive_decline()

    def receive_decline(self, source=None):
        """ Ask the next player in the challenge / counter query list

            This will notify observers if the end of the list has been reached
            source -- the Player who sent the event """
        if source is not None:
            self.message("{} declined".format(source.name))

        try:
            name, next_question = next(self.questions)
            self.message("Asking {}...".format(name))
            next_question()
        except StopIteration:
            self.message("No more players to ask\n")
            for o in self.obs:
                o.notify_decline()

    def receive_accept(self, source):
        """ Notify observers if the challenge / counter was accepted """
        self.message("{} accepted!\n".format(source.name))
        for o in self.obs:
            o.notify_accept(source)

    def resolve_challenge(self, action, challenger):
        """ Prompt action's actor to reveal a card """
        self.message("{}'s {} was challenged by {}!".format(
            action.actor.name, action.name, challenger.name
        ))
        self.challenger = challenger
        self.action = action
        action.actor.resolve_challenge(action)

    def receive_challenge_card(self, actor, card):
        """ Resolve challenge with chosen card, notifying observers of the result """
        self.message("{} revealed {}!".format(actor.name, card.name))
        if self.can_perform(card, self.action):
            self.message("{} was wrong and lost a life!\n".format(self.challenger.name))
            self.challenge_result = lambda: [o.challenge_failed() for o in self.obs]
            wrong_player = self.challenger
        else:
            self.message("{} cannot perform {} and loses a life!\n".format(actor.name, self.action.name))
            self.challenge_result = lambda: [o.challenge_success() for o in self.obs]
            wrong_player = actor

        wrong_player.add_state_observer(self)
        wrong_player.lose_life()

    def notify_lose_life(self, source):
        source.remove_state_observer(self)
        self.challenge_result()

    def can_perform(self, card, action):
        """ Test if card can perform a given action """
        if card == Card.LORD:
            return action.name in ["Tithe", "Counter Donations"]
        elif card == Card.BANDIT:
            return action.name in ["Mug", "Counter Mug"]
        elif card == Card.MERCENARY:
            return action.name in ["Murder"]
        elif card == Card.MEDIC:
            return action.name in ["Counter Murder"]
        elif card == Card.DIPLOMAT:
            return action.name in ["Diplomacy", "Counter Mug"]
        else:
            return False
