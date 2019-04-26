from enum import Enum, auto

class Result(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    BLOCKED = auto()
    CHALLENGE_SUCCESS = auto()
    CHALLENGE_FAILURE = auto()


class Actions(Enum):
    SALARY = auto()
    DONATIONS = auto()
    TITHE = auto()
    DEPOSE = auto()
    MUG = auto()
    MURDER = auto()
    DIPLOMACY = auto()
    COUNTER_DONATIONS = auto()
    COUNTER_MUG = auto()
    COUNTER_MURDER = auto()


class ActionFactory():
    def create(self, action, actor):
        action_map = {
            Actions.SALARY: self.salary,
            Actions.DONATIONS: self.donations,
            Actions.TITHE: self.tithe,
            Actions.DEPOSE: self.depose,
            Actions.MUG: self.mug,
            Actions.MURDER: self.murder,
            Actions.DIPLOMACY: self.diplomacy,
            Actions.COUNTER_DONATIONS: self.counter_donations,
            Actions.COUNTER_MUG: self.counter_mug,
            Actions.COUNTER_MURDER: self.counter_murder
        }

        return action_map[action](actor)

    def salary(self, actor):
        return Salary(actor=actor)

    def donations(self, actor):
        d = Donations(actor=actor)
        return Counterable(d)

    def tithe(self, actor):
        t = Tithe(actor=actor)
        return Questionable(t)

    def depose(self, actor):
        d = Depose(actor=actor)
        return Targeted(d)

    def mug(self, actor):
        m = Mug(actor=actor)
        m = Counterable(m)
        m = Questionable(m)
        return Targeted(m)

    def murder(self, actor):
        m = Murder(actor=actor)
        m = Counterable(m)
        m = Questionable(m)
        return Targeted(m)

    def diplomacy(self, actor):
        dip = Diplomacy(actor=actor)
        return Questionable(dip)

    def counter_donations(self, actor):
        cd = CounterDonations(actor=actor)
        return Questionable(cd)

    def counter_mug(self, actor):
        cm = CounterMug(actor=actor)
        return Questionable(cm)

    def counter_murder(self, actor):
        cm = CounterMurder(actor=actor)
        return Questionable(cm)


""" BASE ACTIONS """
class Action():
    name = "Action"
    description = "Format with {actor}, {target}"

    def __init__(self, actor=None):
        self.actor = actor

    def perform(self, target=None, game=None):
        game.action_completed(self)


class Salary(Action):
    name = "Salary"
    description = "{actor} earned 1 coin"

    def perform(self, target=None, game=None):
        if target is not None:
            raise ValueError("Salary should not be targeted")

        self.actor.coins += 1
        super().perform(target, game)


class Donations(Action):
    name = "Donations"
    description = "{actor} received a donation of 2 coins"

    def perform(self, target=None, game=None):
        if target is not None:
            raise ValueError("Donations should not be targeted")

        self.actor.coins += 2
        super().perform(target, game)


class Tithe(Action):
    name = "Tithe"
    description = "{actor} took a tithe of 3 coins"

    def perform(self, target=None, game=None):
        if target is not None:
            raise ValueError("Tithe should not be targeted")

        self.actor.coins += 3
        super().perform(target, game)


class Depose(Action):
    name = "Depose"
    description = "{actor} deposed {target}"

    def perform(self, target=None, game=None):
        if target is None:
            raise ValueError("Depose must be targeted")

        self.actor.coins -= 7
        target.lose_life()
        super().perform(target, game)


class Mug(Action):
    name = "Mug"
    description = "{actor} mugged {target}"

    def perform(self, target=None, game=None):
        if target is None:
            raise ValueError("Mug must be targeted")

        theft_amount = min(2, target.coins)
        self.actor.coins += theft_amount
        target.coins -= theft_amount
        self.description = "{actor} mugged {target} for " + str(theft_amount) + " coins"

        super().perform(target, game)


class Murder(Action):
    name = "Murder"
    description = "{actor} murdered {target}"

    def perform(self, target=None, game=None):
        if target is None:
            raise ValueError("Murder must be targeted")

        self.actor.coins -= 3
        target.lose_life()
        super().perform(target, game)


class Diplomacy(Action):
    name = "Diplomacy"
    description = "{actor} performed diplomacy"

    def perform(self, target=None, game=None):
        if target is not None:
            raise ValueError("Diplomacy should not be targeted")

        self.actor.draw_cards(2)
        self.actor.return_card()
        self.actor.return_card()
        super().perform(target, game)


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
class ActionModifier(Action):
    def __init__(self, action):
        super().__init__(action.actor)
        self.name = action.name
        self.action = action

    def perform(self, target=None, game=None):
        raise NotImplementedError()


class Targeted(ActionModifier):
    def perform(self, target=None, game=None):
        target = self.actor.choose_target()
        return self.action.perform(target, game)


class Counterable(ActionModifier):
    description = "Check if {actor} is countered"

    def perform(self, target=None, game=None):
        if game is None:
            raise ValueError("Counterable actions require a game reference")

        game.ask_for_counters(self)

    def _perform(self, game, opponent, target=None):
        if opponent is None:
            # No counter > perform action
            self.action.perform(target, game)
        else:
            print("Action was countered")
            counter_action = self.get_counter_action(opponent)
            counter_action.perform(target, game)
            """
                # Counter, not questioned
                return Result.FAILURE
            else:
                # Counter, successfully questioned > perform action
                return self.action.perform(target, game)
            """
    
    def get_counter_action(self, opponent):
        af = ActionFactory()
        if self.name == "Donations":
            counter_action = af.counter_donations(opponent)
        elif self.name == "Mug":
            counter_action = af.counter_mug(opponent)
        elif self.name == "Murder":
            counter_action = af.counter_murder(opponent)
        else:
            raise ValueError("No blocking action exists")

        return counter_action


class Questionable(ActionModifier):
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

    def perform(self, target=None, game=None):
        if game is None:
            raise ValueError("Questionable actions require a game reference")

        opponent = game.ask_for_challenges(self)

    def _perform(self, game, opponent, target=None):
        if opponent is None:
            # No challenge > perform action
            return self.action.perform(target, game)
        else:
            game.resolve_challenge(self)

    def challenge_succeeded(self, game):
        self.action.perform(game=game)

    def is_performed_by(self, card):
        if self.name not in Questionable.action_enablers:
            return False
        else:
            return (card.name in Questionable.action_enablers[self.name])