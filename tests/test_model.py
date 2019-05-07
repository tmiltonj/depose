import pytest
from unittest.mock import Mock

from depose.model import Card, Deck
from depose.player import Player
from depose.actions import ActionFactory

def test_deck():
    deck = Deck()
    
    deck.add(1)
    deck.add(2)
    deck.add(3)
    deck.add(4)

    s = set()
    s.add(deck.get())
    s.add(deck.get())
    s.add(deck.get())
    s.add(deck.get())

    assert 1 in s
    assert 2 in s
    assert 3 in s
    assert 4 in s


@pytest.fixture
def player():
    p = Player("Test Name", action_factory=ActionFactory())
    p.add_card(Card.DIPLOMAT)
    p.add_card(Card.MEDIC)
    p.add_card(Card.LORD)
    return p

@pytest.fixture
def deck():
    d = Deck()
    d.add(Card.BANDIT)
    d.add(Card.MERCENARY)
    return d

class TestPlayer():
    def test_coins(self, player):
        player.coins = 2
        player.coins -= 4

        assert 0 == player.coins

    def test_add_card(self):
        p = Player("Test Name")
        p.add_card(Card.LORD)
        p.add_card(Card.BANDIT)

        assert Card.LORD in p.cards
        assert Card.BANDIT in p.cards
        assert Card.DIPLOMAT not in p.cards

    def test_draw_cards(self, player, deck):
        player.deck = deck
        player.draw_cards(2)

        assert Card.BANDIT in player.cards
        assert Card.MERCENARY in player.cards
        assert 0 == len(deck.cards)

    def test_return_card(self, player, deck):
        player.deck = deck

        player._choose_card = Mock(return_value=Card.DIPLOMAT)

        player.return_card()
        assert Card.DIPLOMAT in deck.cards
        assert 2 == len(player.cards)

        player.return_card(card=Card.MEDIC)
        assert Card.MEDIC in deck.cards
        assert [Card.LORD] == player.cards

        with pytest.raises(ValueError):
            player.return_card()
            player.return_card(Card.BANDIT)

    def test_lose_life(self, player):
        player._choose_card = Mock(return_value=Card.DIPLOMAT)

        assert Card.DIPLOMAT == player.lose_life()
        assert 2 == len(player.cards)
        assert Card.MEDIC == player.lose_life(card=Card.MEDIC)
        assert 1 == len(player.cards)

        with pytest.raises(ValueError):
            player.lose_life()
            player.lose_life(card=Card.MERCENARY)

    def test_get_valid_actions(self, player):
        test_cases = [
            (2, ["Salary", "Donations", "Tithe", "Mug", "Diplomacy"]),
            (6, ["Salary", "Donations", "Tithe", "Mug", "Diplomacy", "Murder"]),
            (9, ["Salary", "Donations", "Tithe", "Mug", "Diplomacy", "Murder", "Depose"])
        ]

        for coins, options in test_cases:
            player.coins = coins
            res = player._get_valid_actions()
            for opt in options:
                assert opt in res.keys(), "{} coins, expected {}".format(coins, options)
        
        player.coins = 11
        res = player._get_valid_actions()
        assert "Depose" in res.keys()
        assert "Salary" not in res.keys()

    def test_choose_action(self, player):
        player.game = Mock()
        player.coins = 7
        actions = [
            "Salary", "Donations", "Tithe", "Depose", "Mug",
            "Murder", "Diplomacy"
        ]

        for a in actions:
            player.game.wait_for_input = Mock(return_value=a)
            act = player.choose_action()
            assert a == act.name