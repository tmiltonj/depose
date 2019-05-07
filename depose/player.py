from depose.view import Option

class Player():
    def __init__(self, name, deck, action_factory, ui):
        self.name = name
        self._coins = 0
        self._cards = []

        self.deck = deck
        self.action_factory = action_factory
        self.ui = ui
        
        self.action_obs = []
        self.target_obs = []
        self.state_obs = []

    @property
    def coins(self):
        return self._coins

    @coins.setter
    def coins(self, value):
        self._coins = max(0, value)

    @property
    def cards(self):
        return self._cards

    def add_card(self, card):
        self._cards.append(card)

    def __str__(self):
        return "{} (Coins: {}, Cards: {})".format(self.name, self._coins, len(self.cards))

    def add_action_observer(self, obs):
        self.action_obs.append(obs)

    def add_target_observer(self, obs):
        self.target_obs.append(obs)

    def add_state_observer(self, obs):
        self.state_obs.append(obs)

    def remove_state_observer(self, obs):
        if obs in self.state_obs:
            self.state_obs.remove(obs)

    def draw_cards(self, number=1):
        for _ in range(number):
            self.add_card(self.deck.get())

    def handle(self, event):
        self.ui.remove_observer(self)
        self.callback(event)

    def callback(self, event):
        pass

    def wait_for_input(self, prompt, optionlist, callback):
        from depose.view import OptionListState
        self.ui.add_observer(self)
        self.callback = callback
        self.ui.set_state(
            OptionListState(self.ui, prompt, optionlist)
        )

    def _cardlist(self):
        cl = []
        for card in self.cards:
            cl.append(Option(card.name, card))
        return cl

    def return_card(self, card=None):
        self.wait_for_input(
            "Select a card to return",
            self._cardlist(),
            self._return_card
        )

    def _return_card(self, card):
        try:
            self.deck.add(card)
            self.cards.remove(card)
            for o in self.state_obs:
                o.notify_return_card(self, card)
        except ValueError:
            print("{}: {} is not in {}".format(self.name, card, self.cards))

    def resolve_challenge(self, action):
        self.wait_for_input(
            "{} was challenged, choose a card to reveal".format(action.name),
            self._cardlist(),
            self._resolve_challenge
        )

    def _resolve_challenge(self, card):
        for o in self.action_obs:
            o.receive_challenge_card(self, card)

    def lose_life(self, card=None):
        if card is None:
            self.wait_for_input(
                "You lost a life, reveal a card",
                self._cardlist(),
                self._lose_life
            )
        else:
            self._lose_life(card)
    
    def _lose_life(self, card):
        self.cards.remove(card)

    def choose_action(self):
        actionlist = self._get_valid_actions()
        self.wait_for_input(
            "Select an action",
            actionlist,
            self._choose_action
        )

    def _choose_action(self, action):
        for o in self.action_obs:
            o.receive_action(
                self.action_factory.create(action, self)
            )

    def _get_valid_actions(self):
        if self.coins >= 10:
            return [Option("Depose", "DEPOSE")]

        actions = [
            Option("Salary", "SALARY"),
            Option("Donations", "DONATIONS"),
            Option("Tithe", "TITHE"),
            Option("Mug", "MUG"),
            Option("Diplomacy", "DIPLOMACY")
        ]

        if self.coins >= 3:
            actions.append(Option("Murder", "MURDER"))
        if self.coins >= 7:
            actions.append(Option("Depose", "DEPOSE"))

        return actions

    def choose_target(self):
        target_list = []
        for p in self.player_list:
            if p is not self and len(p.cards) > 0:
                target_list.append(Option(p.name, p))

        self.wait_for_input(
            "Choose a target",
            target_list,
            self._choose_target
        )

    def _choose_target(self, target):
        for o in self.target_obs:
            o.receive_target(target)

    def ask_to_counter(self, action):
        self.wait_for_input(
            "{}, counter {}'s {}?".format(self.name, action.actor.name, action.name),
            [Option("Yes", True), Option("No", False)],
            self.receive_response
        )

    def ask_to_challenge(self, action):
        choice = self.wait_for_input(
            "{}, challenge {}'s {}?".format(self.name, action.actor.name, action.name),
            [Option("Yes", True), Option("No", False)],
            self.receive_response
        )
    
    def receive_response(self, response):
        if response == True:
            for o in self.action_obs:
                o.receive_accept(self)
        else:
            for o in self.action_obs:
                o.receive_decline(self)
