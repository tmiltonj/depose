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
    def __init__(self, actor, ui, game):
        self.actor = actor
        self.ui = ui
        self.game = game

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
        return Salary(self.actor, self.ui, self.game)

    def donations(self):
        d = Donations(self.actor, self.ui, self.game)
        return Counterable(d)

    def tithe(self):
        t = Tithe(self.actor, self.ui, self.game)
        return Questionable(t)

    def depose(self):
        d = Depose(self.actor, self.ui, self.game)
        return Targeted(d)

    def mug(self):
        m = Mug(self.actor, self.ui, self.game)
        m = Counterable(m)
        m = Questionable(m)
        return Targeted(m)

    def murder(self):
        m = Murder(self.actor, self.ui, self.game)
        m = Counterable(m)
        m = Questionable(m)
        return Targeted(m)

    def diplomacy(self):
        dip = Diplomacy(self.actor, self.ui, self.game)
        return Questionable(dip)

    def counter_donations(self):
        cd = CounterDonations(self.actor, self.ui, self.game)
        return Questionable(cd)

    def counter_mug(self):
        cm = CounterMug(self.actor, self.ui, self.game)
        return Questionable(cm)

    def counter_murder(self):
        cm = CounterMurder(self.actor, self.ui, self.game)
        return Questionable(cm)


""" BASE ACTIONS """
class Action():
    name = "Action"

    def __init__(self, actor, ui, game):
        self.actor = actor
        self.ui = ui
        self.game = game

    def do(self, target=None):
        raise NotImplementedError()


class Salary(Action):
    name = "Salary"

    def do(self, target=None):
        if target is not None:
            raise ValueError("Salary should not be targeted")

        self.actor.coins += 1
        self.ui.message("{} earned 1 coin (Coins: {}).".format(self.actor.name, self.actor.coins))

        return True


class Donations(Action):
    name = "Donations"

    def do(self, target=None):
        if target is not None:
            raise ValueError("Donations should not be targeted")

        self.actor.coins += 2
        self.ui.message("{} received 2 coins (Coins: {}).".format(self.actor.name, self.actor.coins))

        return True


class Tithe(Action):
    name = "Tithe"

    def do(self, target=None):
        if target is not None:
            raise ValueError("Tithe should not be targeted")

        self.actor.coins += 3
        self.ui.message("{} took a tithe of 3 coins (Coins: {}).".format(self.actor.name, self.actor.coins))

        return True


class Depose(Action):
    name = "Depose"

    def do(self, target=None):
        if target is None:
            raise ValueError("Depose must be targeted")

        self.actor.coins -= 7
        self.ui.message("{} deposed {}!".format(self.actor.name, target.name))
        target.lose_life()

        return True


class Mug(Action):
    name = "Mug"

    def do (self, target=None):
        if target is None:
            raise ValueError("Mug must be targeted")

        theft_amount = min(2, target.coins)
        self.actor.coins += theft_amount
        target.coins -= theft_amount
        self.ui.message("{} mugged {} for {} coins!".format(
            self.actor.name, target.name, theft_amount
        ))

        return True


class Murder(Action):
    name = "Murder"

    def do(self, target=None):
        if target is None:
            raise ValueError("Murder must be targeted")

        self.actor.coins -= 3
        self.ui.message("{} murdered {}!".format(self.actor.name, target.name))
        target.lose_life()

        return True


class Diplomacy(Action):
    name = "Diplomacy"

    def do(self, target=None):
        if target is not None:
            raise ValueError("Diplomacy should not be targeted")

        self.ui.message("{} performed diplomacy.".format(self.actor.name))
        self.actor.diplomacy()

        return True


class CounterDonations(Action):
    name = "Counter Donations"

    def do(self, target=None):
        return True


class CounterMug(Action):
    name = "Counter Mug"

    def do(self, target=None):
        return True


class CounterMurder(Action):
    name = "Counter Murder"

    def do(self, target=None):
        return True


""" DECORATORS """
class ActionOption(Action):
    def __init__(self, action):
        super().__init__(action.actor, action.ui, action.game)
        self.name = action.name
        self.action = action

    def do(self, target=None):
        raise NotImplementedError()


class Targeted(ActionOption):
    def do(self, target=None):
        target = self.get_target()
        return self.action.do(target)

    def get_target(self):
        target_list = [p for p in self.game.players if p is not self.actor]
        choice = self.ui.get_choice(
            "Choose a target to {}".format(self.name),
            target_list
        )

        return choice


class Counterable(ActionOption):
    def do(self, target=None):
        blocker = self.get_blocker(target)

        if blocker is None:
            self.ui.message("Action not blocked")
            return self.action.do(target)
        else:
            self.ui.message("{}'s {} was blocked by {}".format(self.actor.name, self.name, blocker.name))
            counter_action = self.get_blocking_action(blocker)
            if counter_action.do(target):
                self.ui.message("Action successfully blocked")
                return False
            else:
                self.ui.message("Performed {}".format(self.name))
                return self.action.do(target)
                

    def get_blocker(self, target=None):
        if target is None:
            blocking_list = [p for p in self.game.players if p is not self.actor]
        else:
            blocking_list = [target]

        for p in blocking_list:
            blocked = self.ui.get_confirm(
                "{}, do you wish to block {}'s {}?".format(p.name, self.actor.name, self.name)
            )

            if blocked:
                return p

        return None
    
    def get_blocking_action(self, blocker):
        af = ActionFactory(blocker, self.ui, self.game)
        if self.name == "Donations":
            counter_action = af.counter_donations()
        elif self.name == "Mug":
            counter_action = af.counter_mug()
        elif self.name == "Murder":
            counter_action = af.counter_murder()
        else:
            raise ValueError("No blocking action exists")

        return counter_action


class Questionable(ActionOption):
    action_enablers = {
        "Tithe": ["Lord"],
        "Mug": ["Bandit"],
        "Murder": ["Mercenary"],
        "Diplomacy": ["Diplomat"],
        "Counter Donations": ["Lord"],
        "Counter Mug": ["Bandit", "Diplomat"],
        "Counter Murder": ["Medic"]
    }

    def do(self, target=None):
        caller = self.get_callout()

        if caller is None:
            return self.action.do(target)
        else:
            self.ui.message("{} called out {}!".format(caller.name, self.name))
            if self.actor.called_out(self):
                caller.lose_life()
                return self.action.do(target)
            else:
                return False

    def get_callout(self):
        calling_list = [p for p in self.game.players if p is not self.actor]
        for p in calling_list:
            called = self.ui.get_confirm(
                "{}, do you wish to call out {}'s {}?".format(p.name, self.actor.name, self.name)
            )

            if called:
                return p

        return None

    def is_performed_by(self, card):
        if self.name not in Questionable.action_enablers:
            return False
        else:
            return (card.name in Questionable.action_enablers[self.name])