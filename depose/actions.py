from enum import Enum, auto

class ActionList(Enum):
    SALARY = auto
    DONATIONS = auto
    TITHE = auto
    DEPOSE = auto
    MUG = auto
    MURDER = auto
    DIPLOMACY = auto
    COUNTER_DONATIONS = auto
    COUNTER_MUG = auto
    COUNTER_MURDER = auto


class ActionFactory():
    def __init__(self, actor=None):
        self.actor = actor

    def create(self, action):
        action_map = {
            ActionList.SALARY: self.salary,
            ActionList.DONATIONS: self.donations,
            ActionList.TITHE: self.tithe,
            ActionList.DEPOSE: self.depose,
            ActionList.MUG: self.mug,
            ActionList.MURDER: self.murder,
            ActionList.DIPLOMACY: self.diplomacy,
            ActionList.COUNTER_DONATIONS: self.counter_donations,
            ActionList.COUNTER_MUG: self.counter_mug,
            ActionList.COUNTER_MURDER: self.counter_murder
        }

        return action_map[action]()

    def salary(self):
        return Salary(actor=self.actor)

    def donations(self):
        d = Donations(actor=self.actor)
        return Counterable(d)

    def tithe(self):
        t = Tithe(actor=self.actor)
        return Questionable(t)

    def depose(self):
        d = Depose(actor=self.actor)
        return Targeted(d)

    def mug(self):
        m = Mug(actor=self.actor)
        m = Counterable(m)
        m = Questionable(m)
        return Targeted(m)

    def murder(self):
        m = Murder(actor=self.actor)
        m = Counterable(m)
        m = Questionable(m)
        return Targeted(m)

    def diplomacy(self):
        dip = Diplomacy(actor=self.actor)
        return Questionable(dip)

    def counter_donations(self):
        cd = CounterDonations(actor=self.actor)
        return Questionable(cd)

    def counter_mug(self):
        cm = CounterMug(actor=self.actor)
        return Questionable(cm)

    def counter_murder(self):
        cm = CounterMurder(actor=self.actor)
        return Questionable(cm)


""" BASE ACTIONS """
class Action():
    name = "Action"
    description = "Format with {actor}, {target}"

    def __init__(self, actor=None):
        self.actor = actor

    def do(self, target=None, game=None):
        return True


class Salary(Action):
    name = "Salary"
    description = "{actor} earned 1 coin"

    def do(self, target=None, game=None):
        if target is not None:
            raise ValueError("Salary should not be targeted")

        self.actor.coins += 1

        return True


class Donations(Action):
    name = "Donations"
    description = "{actor} received a donation of 2 coins"

    def do(self, target=None, game=None):
        if target is not None:
            raise ValueError("Donations should not be targeted")

        self.actor.coins += 2

        return True


class Tithe(Action):
    name = "Tithe"
    description = "{actor} took a tithe of 3 coins"

    def do(self, target=None, game=None):
        if target is not None:
            raise ValueError("Tithe should not be targeted")

        self.actor.coins += 3

        return True


class Depose(Action):
    name = "Depose"
    description = "{actor} deposed {target}"

    def do(self, target=None, game=None):
        if target is None:
            raise ValueError("Depose must be targeted")

        self.actor.coins -= 7
        target.lose_life()

        return True


class Mug(Action):
    name = "Mug"
    description = "{actor} mugged {target}"

    def do (self, target=None, game=None):
        if target is None:
            raise ValueError("Mug must be targeted")

        theft_amount = min(2, target.coins)
        self.actor.coins += theft_amount
        target.coins -= theft_amount
        self.description = "{actor} mugged {target} for " + theft_amount + " coins"

        return True


class Murder(Action):
    name = "Murder"
    description = "{actor} murdered {target}"

    def do(self, target=None, game=None):
        if target is None:
            raise ValueError("Murder must be targeted")

        self.actor.coins -= 3
        target.lose_life()

        return True


class Diplomacy(Action):
    name = "Diplomacy"
    description = "{actor} performed diplomacy"

    def do(self, target=None, game=None):
        if target is not None:
            raise ValueError("Diplomacy should not be targeted")

        self.actor.draw_cards(2)
        self.actor.return_card()
        self.actor.return_card()

        return True


class CounterDonations(Action):
    name = "Counter Donations"
    description = "{actor} sabotaged the donation"

class CounterMug(Action):
    name = "Counter Mug"
    description = "{actor} stopped the mugging"

class CounterMurder(Action):
    name = "Counter Murder"
    description = "{actor} prevented the murder"


""" DECORATORS """
class ActionOption(Action):
    def __init__(self, action):
        super().__init__(action.actor)
        self.name = action.name
        self.action = action

    def do(self, target=None, game=None):
        raise NotImplementedError()


class Targeted(ActionOption):
    def do(self, target=None, game=None):
        target = self.actor.choose_target()
        return self.action.do(target, game)


class Counterable(ActionOption):
    description = "Check if {actor} is countered"

    def do(self, target=None, game=None):
        opponent = game.ask_for_counters(self)
        if opponent is None:
            # No counter > perform action
            return self.action.do(target, game)
        else:
            counter_action = self.get_counter_action(opponent)
            if counter_action.do(target, game):
                # Counter, not questioned
                return False
            else:
                # Counter, successfully questioned > perform action
                return self.action.do(target, game)
    
    def get_counter_action(self, opponent):
        af = ActionFactory()
        if self.name == "Donations":
            counter_action = af.counter_donations()
        elif self.name == "Mug":
            counter_action = af.counter_mug()
        elif self.name == "Murder":
            counter_action = af.counter_murder()
        else:
            raise ValueError("No blocking action exists")

        counter_action.actor = opponent
        return counter_action


class Questionable(ActionOption):
    description = "Check if {actor} is challenged"

    action_enablers = {
        "Tithe": ["Lord"],
        "Mug": ["Bandit"],
        "Murder": ["Mercenary"],
        "Diplomacy": ["Diplomat"],
        "Counter Donations": ["Lord"],
        "Counter Mug": ["Bandit", "Diplomat"],
        "Counter Murder": ["Medic"]
    }

    def do(self, target=None, game=None):
        opponent = game.ask_for_challenges(self)

        if opponent is None:
            # No challenge > perform action
            return self.action.do(target, game)
        elif game.resolve_challenge(opponent, self):
            # Challenged successfully (actor did not reveal correct card)
            return False
        else:
            # Challenge failed (actor did reveal correct card) > perform action
            return self.action.do(target)

    def is_performed_by(self, card):
        if self.name not in Questionable.action_enablers:
            return False
        else:
            return (card.name in Questionable.action_enablers[self.name])