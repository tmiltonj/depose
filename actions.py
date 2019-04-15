class ActionFactory():
    @staticmethod
    def salary(actor):
        return Salary(actor)

    @staticmethod
    def donations(actor):
        fa = Donations(actor)
        return Blockable(fa)

    @staticmethod
    def tithe(actor):
        tx = Tithe(actor)
        return Callable(tx)

    @staticmethod
    def depose(actor):
        cp = Depose(actor)
        return Targeted(cp)

    @staticmethod
    def mug(actor):
        st = Mug(actor)
        st = Blockable(st)
        st = Callable(st)
        return Targeted(st)

    @staticmethod
    def murder(actor):
        assn = Murder(actor)
        assn = Blockable(assn)
        assn = Callable(assn)
        return Targeted(assn)

    @staticmethod
    def diplomacy(actor):
        amb = Diplomacy(actor)
        return Callable(amb)


""" BASE ACTIONS """
class Action():
    def __init__(self, actor):
        self.actor = actor

    def do(self, target=None):
        raise NotImplementedError()


class Salary(Action):
    def do(self, target=None):
        if target is not None:
            raise ValueError("Salary should not be targeted")

        self.actor.coins += 1


class Donations(Action):
    def do(self, target=None):
        if target is not None:
            raise ValueError("Donations should not be targeted")

        self.actor.coins += 1


class Tithe(Action):
    def do(self, target=None):
        if target is not None:
            raise ValueError("Tithe should not be targeted")

        self.actor.coins += 3


class Depose(Action):
    def do(self, target=None):
        if target is None:
            raise ValueError("Depose must be targeted")

        self.actor.coins -= 7
        target.lose_life()


class Mug(Action):
    def do (self, target=None):
        if target is None:
            raise ValueError("Mug must be targeted")

        theft_amount = min(2, target.coins)
        self.actor.coins += theft_amount
        target.coins -= theft_amount


class Murder(Action):
    def do(self, target=None):
        if target is None:
            raise ValueError("Murder must be targeted")

        self.actor.coins -= 3
        target.lose_life()


class Diplomacy(Action):
    def do(self, target=None):
        if target is not None:
            raise ValueError("Diplomacy should not be targeted")

        self.actor.diplomacy()


""" DECORATORS """
class ActionOption(Action):
    def __init__(self, action):
        super().__init__(action.actor)
        self.action = action

    def do(self, target=None):
        raise NotImplementedError()


class Targeted(ActionOption):
    def do(self, target=None):
        player = Player()
        target = player # Select a target
        print("Select a target")
        self.action.do(target)


class Blockable(ActionOption):
    def do(self, target=None):
        blocker = None
        if target is None:
            print("Ask if any player blocks")
        else:
            print("Ask if target blocks")

        if blocker is None:
            self.action.do(target)
        else:
            print("Ask to call out blocker")


class Callable(ActionOption):
    def do(self, target=None):
        caller = None 
        print("Ask if any player calls out the action")

        if caller is None:
            self.action.do(target)
        else:
            print("Call out action")


if __name__ == '__main__':
    from depose import Player
    player = Player()
    af = ActionFactory

    actions = [
        ("Salary", af.salary(player)),    
        ("Donations", af.donations(player)),
        ("Tithe", af.tithe(player)),
        ("Depose", af.depose(player)),
        ("Mug", af.mug(player)),
        ("Murder", af.murder(player)),
        ("Diplomacy", af.diplomacy(player))
    ]

    for name, act in actions:
        print("\nTesting " + name)
        act.do()