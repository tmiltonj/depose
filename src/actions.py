class ActionFactory():
    def __init__(self, actor, ui, game):
        self.actor = actor
        self.ui = ui
        self.game = game

    def salary(self):
        return Salary(self.actor, self.ui, self.game)

    def donations(self):
        fa = Donations(self.actor, self.ui, self.game)
        return Blockable(fa)

    def tithe(self):
        tx = Tithe(self.actor, self.ui, self.game)
        return Callable(tx)

    def depose(self):
        cp = Depose(self.actor, self.ui, self.game)
        return Targeted(cp)

    def mug(self):
        st = Mug(self.actor, self.ui, self.game)
        st = Blockable(st)
        st = Callable(st)
        return Targeted(st)

    def murder(self):
        assn = Murder(self.actor, self.ui, self.game)
        assn = Blockable(assn)
        assn = Callable(assn)
        return Targeted(assn)

    def diplomacy(self):
        amb = Diplomacy(self.actor, self.ui, self.game)
        return Callable(amb)

    def block_donations(self):
        bd = BlockDonations(self.actor, self.ui, self.game)
        return Callable(bd)

    def block_mug(self):
        bm = BlockMug(self.actor, self.ui, self.game)
        return Callable(bm)

    def block_murder(self):
        bm = BlockMurder(self.actor, self.ui, self.game)
        return Callable(bm)


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


class BlockDonations(Action):
    name = "Block Donations"

    def do(self, target=None):
        return True


class BlockMug(Action):
    name = "Block Mug"

    def do(self, target=None):
        return True


class BlockMurder(Action):
    name = "Block Murder"

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


class Blockable(ActionOption):
    def do(self, target=None):
        blocker = self.get_blocker(target)

        if blocker is None:
            self.ui.message("Action not blocked")
            return self.action.do(target)
        else:
            self.ui.message("{}'s {} was blocked by {}".format(self.actor.name, self.name, blocker.name))
            block_action = self.get_blocking_action(blocker)
            if block_action.do(target):
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
            block_action = af.block_donations()
        elif self.name == "Mug":
            block_action = af.block_mug()
        elif self.name == "Murder":
            block_action = af.block_murder()
        else:
            raise ValueError("No blocking action exists")

        return block_action


class Callable(ActionOption):
    action_enablers = {
        "Tithe": ["Lord"],
        "Mug": ["Bandit"],
        "Murder": ["Mercenary"],
        "Diplomacy": ["Diplomat"],
        "Block Donations": ["Lord"],
        "Block Mug": ["Bandit", "Diplomat"],
        "Block Murder": ["Medic"]
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
        if self.name not in Callable.action_enablers:
            return False
        else:
            return (card.name in Callable.action_enablers[self.name])


if __name__ == '__main__':
    import view, model
    from depose import Player
    player = Player(view.UI(), model.Deck())
    ui = view.UI()
    af = ActionFactory(player, ui)

    actions = [
        ("Salary", af.salary()),    
        ("Donations", af.donations()),
        ("Tithe", af.tithe()),
        ("Depose", af.depose()),
        ("Mug", af.mug()),
        ("Murder", af.murder()),
        ("Diplomacy", af.diplomacy())
    ]

    for name, act in actions:
        print("\nTesting " + name)
        act.do()