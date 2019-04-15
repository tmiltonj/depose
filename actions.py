class ActionFactory():
    @staticmethod
    def income(actor):
        return Income(actor)

    @staticmethod
    def foreign_aid(actor):
        fa = ForeignAid(actor)
        return Blockable(fa)

    @staticmethod
    def tax(actor):
        tx = Tax(actor)
        return Callable(tx)

    @staticmethod
    def coup(actor):
        cp = Coup(actor)
        return Targeted(cp)

    @staticmethod
    def steal(actor):
        st = Steal(actor)
        st = Blockable(st)
        st = Callable(st)
        return Targeted(st)

    @staticmethod
    def assassinate(actor):
        assn = Assassinate(actor)
        assn = Blockable(assn)
        assn = Callable(assn)
        return Targeted(assn)

    @staticmethod
    def ambassador(actor):
        amb = Ambassador(actor)
        return Callable(amb)


""" BASE ACTIONS """
class Action():
    def __init__(self, actor):
        self.actor = actor

    def do(self, target=None):
        raise NotImplementedError()


class Income(Action):
    def do(self, target=None):
        if target is not None:
            raise ValueError("Income should not be targeted")

        self.actor.coins += 1


class ForeignAid(Action):
    def do(self, target=None):
        if target is not None:
            raise ValueError("Foreign Aid should not be targeted")

        self.actor.coins += 1


class Tax(Action):
    def do(self, target=None):
        if target is not None:
            raise ValueError("Tax should not be targeted")

        self.actor.coins += 3


class Coup(Action):
    def do(self, target=None):
        if target is None:
            raise ValueError("Coup must be targeted")

        self.actor.coins -= 7
        target.lose_life()


class Steal(Action):
    def do (self, target=None):
        if target is None:
            raise ValueError("Steal must be targeted")

        theft_amount = min(2, target.coins)
        self.actor.coins += theft_amount
        target.coins -= theft_amount


class Assassinate(Action):
    def do(self, target=None):
        if target is None:
            raise ValueError("Assassinate must be targeted")

        self.actor.coins -= 3
        target.lose_life()


class Ambassador(Action):
    def do(self, target=None):
        if target is not None:
            raise ValueError("Ambassador should not be targeted")

        self.actor.ambassador()


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
    from coup import Player
    player = Player()
    af = ActionFactory

    actions = [
        ("Income", af.income(player)),    
        ("Foreign Aid", af.foreign_aid(player)),
        ("Tax", af.tax(player)),
        ("Coup", af.coup(player)),
        ("Steal", af.steal(player)),
        ("Assassinate", af.assassinate(player)),
        ("Ambassador", af.ambassador(player))
    ]

    for name, act in actions:
        print("\nTesting " + name)
        act.do()