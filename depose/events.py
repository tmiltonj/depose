from functools import partial

from depose.model import Card

def main():
    g = Game()
    g.play()


class Game():
    def __init__(self):
        self.players = [
            Player("A"),
            Player("B"),
            Player("C"),
            Player("D")
        ]

        for p in self.players:
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


class Action():
    def __init__(self, actor, name):
        self.actor = actor
        self.name = name
        self.obs = []
        self.dec_obs = []

    def add_observer(self, obs):
        print("adding", getattr(obs, "name", "Game"), "as an obs to", self.name)
        self.obs.append(obs)

    def add_decorator_observer(self, obs):
        print("adding", getattr(obs, "name", "Game"), "as a dec_obs to", self.name)
        self.dec_obs.append(obs)

    def get_observers(self):
        return self.obs

    def get_decorator_observers(self):
        return self.dec_obs

    def perform(self, target=None):
        print("Performing action...")
        self.notify_success()

    def notify_success(self):
        for o in self.get_observers():
            o.action_success(self)
        
    def notify_failure(self):
        for o in self.get_observers():
            o.action_failed(self)

#TODO: concrete implementations in actions.py

class ActionDecorator(Action):
    """ Decorate Actions to allow targetting, countering and challenging """
    def __init__(self, base_action):
        super().__init__(base_action.actor, base_action.name)
        self.base_action = base_action

    def add_observer(self, obs):
        self.base_action.add_observer(obs)

    def add_decorator_observer(self, obs):
        self.base_action.add_decorator_observer(obs)

    def get_observers(self):
        return self.base_action.get_observers()

    def get_decorator_observers(self):
        return self.base_action.get_decorator_observers()

    def stop_listening(self):
        """ Stop listening for future counter / challenge responses """
        for o in self.get_decorator_observers():
            o.remove_observer(self)


class TargetAction(ActionDecorator):
    """ Ensures base_action has a target before it's performed """
    def perform(self, target=None):
        if target is None:
            self.actor.add_target_observer(self)
            self.actor.choose_target()
        else:
            self.receive_target(target)

    def receive_target(self, target):
        print("TargetAction: targetting", target)
        self.base_action.perform(target)


class ChallengeAction(ActionDecorator):
    """ Allows all other players to challenge an action before it's performed """
    def perform(self, target=None):
        self.target = target
        for o in self.get_decorator_observers():
            print("ChallengeAction: Adding", getattr(o, "name", "Game"), "as an obs")
            o.add_observer(self) # Listen for the result of the following query
            o.ask_for_challenges(self)

    def notify_accept(self, challenger):
        """ Challenger accepts """
        print(self.name, "was challenged by", challenger.name)
        for o in self.get_decorator_observers():
            o.resolve_challenge(self, challenger)
        
    def notify_decline(self):
        """ No challenge found, we perform the action """
        print(self.name, "was not challenged")
        self.challenge_failed()

    def challenge_success(self):
        """ Challenge succeeded (we revealed the wrong card) """
        print(self.actor.name, "could not complete", self.name)
        self.stop_listening()
        self.notify_failure()

    def challenge_failed(self):
        """ Challenge failed, we can perform the action """
        print("{} can {}!".format(self.actor.name, self.name))
        self.stop_listening()
        self.base_action.perform(target=self.target)


class CounterableAction(ActionDecorator):
    """ Allows other players to counter an action before it's performed """
    def perform(self, target=None):
        self.target = target
        for o in self.get_decorator_observers():
            print("CounterableAction: Adding", getattr(o, 'name', 'Game'), "as an obs")
            o.add_observer(self) # Listen to the result of the following query
            o.ask_for_counters(self)

    def get_counter_action(self, actor):
        """ Return matching counter-action """
        if self.name == "donations":
            name = "block donations"
        elif self.name == "mug":
            name = "block mug"
        elif self.name == "murder":
            name = "block murder"
        else:
            raise ValueError("Action has no counter")

        a = Action(name=name, actor=actor)
        return ChallengeAction(base_action=a)

    def notify_accept(self, opponent):
        """ Counter accepted. Create, perform and listen to the counter-action """
        print(self.name, "was countered by", opponent.name)
        counter = self.get_counter_action(actor=opponent)
        counter.add_observer(self)
        # The counter-action needs to ask for challenges
        for o in self.get_decorator_observers():
            counter.add_decorator_observer(o) 
        self.stop_listening() # we don't want to hear the response though
        counter.perform()
    
    def notify_decline(self):
        """ Nobody chose to counter, so we perform our base_action """
        print(self.name, "was not countered")
        self.action_failed(None)

    def action_success(self, action):
        """ Counter succeeded (which stops this action) """
        print(self.name, "was countered")
        self.stop_listening()
        self.notify_failure()

    def action_failed(self, action):
        """ Counter failed, we can perform this action """
        print(self.name, "could not be countered")
        self.stop_listening()
        self.base_action.perform(target=self.target)


class Player():
    # TODO: Hook input methods into GUI
    def __init__(self, name):
        self.name = name
        self.action_obs = []
        self.target_obs = []

    def add_action_observer(self, obs):
        self.action_obs.append(obs)

    def add_target_observer(self, obs):
        self.target_obs.append(obs)

    def choose_action(self):
        action_name = input("Type an action: ")
        a = Action(actor=self, name=action_name)
        b = CounterableAction(base_action=a)
        c = ChallengeAction(base_action=b)
        t = TargetAction(base_action=c)
        for o in self.action_obs:
            o.receive_action(t)

    def choose_target(self):
        target_name = input("Choose a target: ")
        for o in self.target_obs:
            o.receive_target(self)

    def ask_to_challenge(self, action):
        choice = input("{}, do you wish to challenge {}'s {}? ".format(
            self.name, action.actor.name, action.name
        ))
        if len(choice) > 0 and choice.upper()[0] == "Y":
            for o in self.action_obs:
                o.receive_accept(self)
        else:
            for o in self.action_obs:
                o.receive_decline(self)

    def ask_to_counter(self, action):
        choice = input("{}, do you wish to counter {}'s {}? ".format(
            self.name, action.actor.name, action.name
        ))
        if len(choice) > 0 and choice.upper()[0] == "Y":
            for o in self.action_obs:
                o.receive_accept(self)
        else:
            for o in self.action_obs:
                o.receive_decline(self)

    def resolve_challenge(self, action):
        choices = [Card.LORD, Card.BANDIT, Card.MERCENARY]
        print(choices)
        ind = -1
        while ind < 0 or ind >= len(choices):
            try:
                ind = int(input("Pick a card: "))
            except ValueError:
                ind = -1

        for o in self.action_obs:
            o.receive_challenge_card(self, choices[ind])



if __name__ == '__main__':
    main()