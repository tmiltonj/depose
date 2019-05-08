class ActionFactory():
    def create(self, action, actor):
        action_map = {
            'SALARY': self.salary,
            'DONATIONS': self.donations,
            'TITHE': self.tithe,
            'DEPOSE': self.depose,
            'MUG': self.mug,
            'MURDER': self.murder,
            'DIPLOMACY': self.diplomacy,
            'COUNTER DONATIONS': self.counter_donations,
            'COUNTER MUG': self.counter_mug,
            'COUNTER MURDER': self.counter_murder
        }

        return action_map[action.upper()](actor)

    def salary(self, actor):
        return Salary(actor=actor)

    def donations(self, actor):
        d = Donations(actor=actor)
        return CounterableAction(d)

    def tithe(self, actor):
        t = Tithe(actor=actor)
        return ChallengableAction(t)

    def depose(self, actor):
        d = Depose(actor=actor)
        return TargetedAction(d)

    def mug(self, actor):
        m = Mug(actor=actor)
        m = CounterableAction(m)
        m = ChallengableAction(m)
        return TargetedAction(m)

    def murder(self, actor):
        m = Murder(actor=actor)
        m = CounterableAction(m)
        m = ChallengableAction(m)
        return TargetedAction(m)

    def diplomacy(self, actor):
        dip = Diplomacy(actor=actor)
        return ChallengableAction(dip)

    def counter_donations(self, actor):
        cd = CounterDonations(actor=actor)
        return ChallengableAction(cd)

    def counter_mug(self, actor):
        cm = CounterMug(actor=actor)
        return ChallengableAction(cm)

    def counter_murder(self, actor):
        cm = CounterMurder(actor=actor)
        return ChallengableAction(cm)


class Action():
    """ Base class for Actions """
    name = "Base Action"
    description = ""

    def __init__(self, actor):
        self.actor = actor
        self.obs = []
        self.dec_obs = []

    def add_observer(self, obs):
        print("{}: {} is now listening".format(self.name, getattr(obs, "name", "Game")))
        self.obs.append(obs)

    def add_decorator_observer(self, obs):
        print("{}: {} is now listening (decorator_obs)".format(self.name, getattr(obs, "name", "Game")))
        self.dec_obs.append(obs)

    def remove_observer(self, obs):
        obs_list = self.get_observers()
        if obs in obs_list:
            print("{}: {} stopped listening".format(self.name, getattr(obs, "name", "Game")))
            obs_list.remove(obs)

    def remove_decorator_observer(self, obs):
        obs_list = self.get_decorator_observers()
        if obs in obs_list:
            print("{}: {} stopped listening (decorator_obs)".format(self.name, getattr(obs, "name", "Game")))
            obs_list.remove(obs)

    def get_observers(self):
        return self.obs

    def get_decorator_observers(self):
        return self.dec_obs

    def perform(self, target=None):
        print("{}: {}".format(self.name, self.description))
        self.notify_success()

    def notify_success(self):
        for o in self.get_observers():
            o.action_success(self)
        
    def notify_failure(self):
        for o in self.get_observers():
            o.action_failed(self)


class Salary(Action):
    name = "Salary"
    description = "{actor} earned 1 coin"

    def perform(self, target=None):
        if target is not None:
            raise ValueError("Salary should not be targeted")

        self.actor.coins += 1
        super().perform(target)


class Donations(Action):
    name = "Donations"
    description = "{actor} received a donation of 2 coins"

    def perform(self, target=None):
        if target is not None:
            raise ValueError("Donations should not be targeted")

        self.actor.coins += 2
        super().perform(target)


class Tithe(Action):
    name = "Tithe"
    description = "{actor} took a tithe of 3 coins"

    def perform(self, target=None):
        if target is not None:
            raise ValueError("Tithe should not be targeted")

        self.actor.coins += 3
        super().perform(target)


class Depose(Action):
    name = "Depose"
    description = "{actor} deposed {target}"

    def perform(self, target=None):
        if target is None:
            raise ValueError("Depose must be targeted")

        self.actor.coins -= 7
        target.lose_life()
        super().perform(target)


class Mug(Action):
    name = "Mug"
    description = "{actor} mugged {target}"

    def perform(self, target=None):
        if target is None:
            raise ValueError("Mug must be targeted")

        theft_amount = min(2, target.coins)
        self.actor.coins += theft_amount
        target.coins -= theft_amount
        self.description = "{actor} mugged {target} for " + str(theft_amount) + " coins"

        super().perform(target)


class Murder(Action):
    name = "Murder"
    description = "{actor} murdered {target}"

    def perform(self, target=None):
        if target is None:
            raise ValueError("Murder must be targeted")

        self.actor.coins -= 3
        target.lose_life()
        super().perform(target)


class Diplomacy(Action):
    name = "Diplomacy"
    description = "{actor} performed diplomacy"

    def __init__(self, actor):
        super().__init__(actor)
        self.returned_count = 0

    def perform(self, target=None):
        self.target = target
        if target is not None:
            raise ValueError("Diplomacy should not be targeted")

        self.actor.add_state_observer(self)
        self.actor.draw_cards(2)
        self.actor.return_card()

    def notify_return_card(self, actor, card):
        if actor is not self.actor:
            raise ValueError("Unexpected actor:", actor)

        self.returned_count += 1
        print("{}: {} returned {}".format(self.name, self.actor.name, card.name))
        if self.returned_count < 2:
            self.actor.return_card()
        else:
            self.actor.remove_state_observer(self)
            super().perform(self.target)


class CounterDonations(Action):
    name = "Counter Donations"
    description = "{actor} sabotaged the donation"

class CounterMug(Action):
    name = "Counter Mug"
    description = "{actor} stopped the mugging"

class CounterMurder(Action):
    name = "Counter Murder"
    description = "{actor} prevented the murder"


class ActionDecorator(Action):
    """ Decorate Actions to allow targetting, countering and challenging """
    def __init__(self, base_action):
        super().__init__(base_action.actor)
        self.base_action = base_action

    @property
    def name(self):
        return self.base_action.name    

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
            print("{}: Stopped listening to {}".format(self.name, getattr(o, "name", "Game")))
            o.remove_observer(self)


class TargetedAction(ActionDecorator):
    """ Ensures base_action has a target before it's performed """
    def perform(self, target=None):
        if target is None:
            self.actor.add_target_observer(self)
            self.actor.choose_target()
        else:
            self.receive_target(target)

    def receive_target(self, target):
        print("{}: Targeting".format(self.name), target)
        self.actor.remove_target_observer(self)
        self.base_action.perform(target)


class ChallengableAction(ActionDecorator):
    """ Allows all other players to challenge an action before it's performed """
    def perform(self, target=None):
        self.target = target
        for o in self.get_decorator_observers():
            print("{}: Listening to {}".format(self.name, getattr(o, "name", "Game")))
            o.add_observer(self) # Listen for the result of the following query
            o.ask_for_challenges(self)

    def notify_accept(self, challenger):
        """ Challenger accepts """
        print("{}: Attempted challenge by {}".format(self.name, challenger.name))
        for o in self.get_decorator_observers():
            o.resolve_challenge(self, challenger)
        
    def notify_decline(self):
        """ No challenge found, we perform the action """
        self.challenge_failed()

    def challenge_success(self):
        """ Challenge succeeded (we revealed the wrong card) """
        print("{}: Challenged successfully, cannot perform".format(self.name))
        self.stop_listening()
        self.notify_failure()

    def challenge_failed(self):
        """ Challenge failed, we can perform the action """
        print("{}: Was not challenged / challenge failed".format(self.name))
        self.stop_listening()
        self.base_action.perform(target=self.target)


class CounterableAction(ActionDecorator):
    """ Allows other players to counter an action before it's performed """
    def perform(self, target=None):
        self.target = target
        for o in self.get_decorator_observers():
            print("{}: Listening to {}".format(self.name, getattr(o, "name", "Game")))
            o.add_observer(self) # Listen to the result of the following query
            o.ask_for_counters(self)

    def get_counter_action(self, actor):
        """ Return matching counter-action """
        af = ActionFactory()
        if self.name == "Donations":
            counter = af.counter_donations(actor)
        elif self.name == "Mug":
            counter = af.counter_mug(actor)
        elif self.name == "Murder":
            counter = af.counter_murder(actor)
        else:
            raise ValueError("Action has no counter")

        return counter

    def notify_accept(self, opponent):
        """ Counter accepted. Create, perform and listen to the counter-action """
        print("{}: Attempted counter by {}".format(self.name, opponent.name))
        counter = self.get_counter_action(actor=opponent)
        counter.add_observer(self)
        # The counter-action needs to ask for challenges
        for o in self.get_decorator_observers():
            counter.add_decorator_observer(o) 
        self.stop_listening() # we don't want to hear the response though
        counter.perform()
    
    def notify_decline(self):
        """ Nobody chose to counter, so we perform our base_action """
        self.action_failed(None)

    def action_success(self, action):
        """ Counter succeeded (which stops this action) """
        print("{}: Was countered".format(self.name))
        self.stop_listening()
        self.notify_failure()

    def action_failed(self, action):
        """ Counter failed, we can perform this action """
        print("{}: Was not countered".format(self.name))
        self.stop_listening()
        self.base_action.perform(target=self.target)
