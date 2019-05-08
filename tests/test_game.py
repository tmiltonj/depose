import pytest
from unittest.mock import MagicMock

from depose.actions import ActionFactory, Mug
from depose.player import Player
from depose.game import Game
from depose.model import Card, Deck

@pytest.fixture
def ui():
    class UI():
        def add_observer(self, obs):
            pass

        def remove_observer(self, obs):
            pass
        
        def message(self, message):
            pass

    return UI()

@pytest.fixture
def deck():
    d = Deck()
    d.add(Card.LORD)
    d.add(Card.BANDIT)
    return d

@pytest.fixture
def player(deck, action_factory, ui):
    p = Player("Test Player", deck, action_factory, ui)
    return p

@pytest.fixture
def game(player, ui):
    g = Game([player], ui)
    return g

@pytest.fixture
def action_factory():
    af = ActionFactory()
    return af

@pytest.fixture
def action(player):
    return Mug(player)


def test_cleanup(player, deck, action_factory, ui):
    player.draw_cards(1)
    alive_player = Player("Alive Player", deck, action_factory, ui)
    alive_player.draw_cards(1)
    dead_player = Player("Dead Player", deck, action_factory, ui)

    game = Game([player, alive_player, dead_player], ui)
    game.play = MagicMock()
    game.active_player = game.turn_queue.popleft()
    game.cleanup()

    assert player in game.turn_queue
    assert alive_player in game.turn_queue
    assert dead_player not in game.turn_queue
    game.play.assert_called_once()

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
