import pytest
from unittest.mock import Mock, MagicMock

from depose.model import Deck, Card
from depose.player import Player
from depose.actions import (
    ActionFactory, 
    Salary, Donations, Tithe, Depose, Mug, Murder, Diplomacy,
    TargetedAction, CounterableAction, ChallengableAction,
)

@pytest.fixture
def ui():
    class UI():
        def add_observer(self, obs):
            pass

        def remove_observer(self, obs):
            pass

    return UI()

@pytest.fixture
def deck():
    d = Deck()
    d.add(Card.LORD)
    d.add(Card.BANDIT)
    return d

@pytest.fixture
def action_factory():
    return ActionFactory()

@pytest.fixture
def player(deck, action_factory, ui):
    p = Player("Test Player", deck, action_factory, ui)
    p.coins = 2
    p.add_card(Card.MEDIC)
    p.add_card(Card.MERCENARY)
    return p

@pytest.fixture
def target(deck, action_factory, ui):
    p = Player("Test Target", deck, action_factory, ui)
    p.coins = 3
    p.add_card(Card.BANDIT)
    p.add_card(Card.MEDIC)
    return p


def test_actionfactory(action_factory, player):
    actions = [
        "Salary", "Donations", "Tithe", "Depose",
        "Mug", "Murder", "Diplomacy",
        "Counter Donations", "Counter Mug", "Counter Murder"
    ]
    for action in actions:
        act = action_factory.create(action, player)
        assert act.name == action

""" Test Base Actions """
def test_salary(player):
    a = Salary(actor=player)
    a.perform()
    assert 3 == player.coins
    with pytest.raises(ValueError):
        a.perform(target=player)

def test_donations(player):
    a = Donations(actor=player)
    a.perform()
    assert 4 == player.coins
    with pytest.raises(ValueError):
        a.perform(target=player)

def test_tithe(player):
    a = Tithe(actor=player)
    a.perform()
    assert 5 == player.coins
    with pytest.raises(ValueError):
        a.perform(target=player)

def test_depose(player, target):
    a = Depose(actor=player)
    target.lose_life = Mock()
    a.perform(target=target)
    target.lose_life.assert_called_once()
    with pytest.raises(ValueError):
        a.perform()

def test_mug(player, target):
    a = Mug(actor=player)
    a.perform(target=target)
    assert 1 == target.coins
    assert 4 == player.coins

    a.perform(target=target)
    assert 5 == player.coins

    with pytest.raises(ValueError):
        a.perform()

def test_murder(player):
    a = Murder(actor=player)
    player.lose_life = Mock()
    player.coins = 5

    a.perform(target=player)
    assert 2 == player.coins
    player.lose_life.assert_called_once()
    with pytest.raises(ValueError):
        a.perform()


""" Test Modifiers """
@pytest.fixture
def action(player):
    a = Mug(actor=player)
    return a

def test_targeted(action, player, target):
    player.choose_target = Mock()
    a = TargetedAction(action)
    a.perform()
    player.choose_target.assert_called_once()

def test_counterable(player, action, target):
    action.perform = MagicMock()
    a = CounterableAction(action)
    mock_obs = MagicMock()
    a.add_decorator_observer(mock_obs)

    # Test that it asks for counter correctly
    a.perform(target=target)
    mock_obs.ask_for_counters.assert_called_once()

    # No counters > perform action normally
    a.notify_decline()
    action.perform.assert_called_once()

    # Counter accepted > check the counter action is performed
    counter_action = MagicMock()
    a.get_counter_action = MagicMock(return_value=counter_action)
    a.notify_accept(target)
    counter_action.perform.assert_called_once()

    # Counter successful > don't perform base_action
    action.perform.reset_mock()
    a.action_success(None)
    action.perform.assert_not_called()

    # Counter failed  > perform base_action
    action.perform.reset_mock()
    a.action_failed(None)
    action.perform.assert_called_once()
   

def test_questionable(player, action, target):
    action.perform = MagicMock()
    a = ChallengableAction(action)
    mock_obs = MagicMock()
    a.add_decorator_observer(mock_obs)

    # Test that it asks for counter correctly
    a.perform(target=target)
    mock_obs.ask_for_challenges.assert_called_once()

    # No counters > perform action normally
    a.notify_decline()
    action.perform.assert_called_once()

    # Challenge accepted > check the challenge action is performed
    a.notify_accept(target)
    mock_obs.resolve_challenge.assert_called_once()

    # Counter successful > don't perform base_action
    action.perform.reset_mock()
    a.challenge_success()
    action.perform.assert_not_called()

    # Counter failed  > perform base_action
    action.perform.reset_mock()
    a.challenge_failed()
    action.perform.assert_called_once()