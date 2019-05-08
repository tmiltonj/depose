import pytest

from depose.actions import ActionFactory
from depose.player import Player
from depose.game import Game
from depose.model import Card

@pytest.fixture
def player():
    p = Player("Test Player", None, None, None)
    return p

@pytest.fixture
def game(player):
    g = Game([player], None)
    return g

@pytest.fixture
def action_factory():
    af = ActionFactory()
    return af

def test_can_perform(player, game, action_factory):
    af = action_factory
    test_cases = [
        (Card.LORD, af.tithe(player)),
        (Card.LORD, af.counter_donations(player)),
        (Card.BANDIT, af.mug(player)),
        (Card.BANDIT, af.counter_mug(player)),
        (Card.MERCENARY, af.murder(player)),
        (Card.MEDIC, af.counter_murder(player)),
        (Card.DIPLOMAT, af.diplomacy(player)),
        (Card.DIPLOMAT, af.counter_mug(player))
    ]

    for card, action in test_cases:
        assert game.can_perform(card, action), "{} can perform {}".format(card, action.name)

    test_cases = [
        (Card.LORD, af.murder(player)),
        (Card.MEDIC, af.mug(player)),
        (Card.BANDIT, af.diplomacy(player)),
        (Card.MERCENARY, af.counter_donations(player)),
        (Card.DIPLOMAT, af.mug(player))
    ]

    for card, action in test_cases:
        assert not game.can_perform(card, action), "{} cannot perform {}".format(card, action.name)
