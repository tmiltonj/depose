import pytest
from unittest.mock import MagicMock, ANY

from depose.player import Player
from depose.model import Deck, Card
from depose.actions import ActionFactory
from depose.view import Option

@pytest.fixture
def deck():
    d = Deck()
    d.add(Card.MEDIC)
    d.add(Card.MERCENARY)
    return d

@pytest.fixture
def action_factory():
    return ActionFactory()

@pytest.fixture
def ui():
    class UI():
        def add_observer(self, obs):
            pass

        def remove_observer(self, obs):
            pass

    return UI()

@pytest.fixture
def player(deck, action_factory, ui):
    p = Player("Test Name", deck, action_factory, ui)
    p.add_card(Card.LORD)
    p.add_card(Card.BANDIT)
    p.coins = 2
    return p

@pytest.fixture
def action_obs(player):
    obs = MagicMock()
    player.add_action_observer(obs)
    return obs

@pytest.fixture
def state_obs(player):
    obs = MagicMock()
    player.add_state_observer(obs)
    return obs

def test_coins(player):
    player.coins = 3
    player.coins -= 4
    assert 0 == player.coins

    player.coins = 10
    player.coins -= 2
    assert 8 == player.coins

def test_add_card(player):
    player.add_card(Card.MEDIC)
    player.add_card(Card.MERCENARY)

    assert Card.MEDIC in player.cards
    assert Card.DIPLOMAT not in player.cards

def test_draw_cards(player, deck):
    player.deck = deck
    player.draw_cards(2)

    assert Card.MEDIC in player.cards
    assert Card.MERCENARY in player.cards
    assert 0 == len(deck.cards)

def test_observers(player, state_obs):
    player.remove_state_observer(state_obs)
    assert state_obs not in player.state_obs

def test_wait_for_input(player, ui):
    ui.set_state = MagicMock()
    fake_callback = MagicMock()

    player.wait_for_input(
        "Test",
        [Option("Yes", True), Option("No", False)],
        fake_callback
    )
    player.handle("Event")

    ui.set_state.assert_called_once()
    fake_callback.assert_called_once_with("Event")

def test_cardlist(player):
    cardlist = player._cardlist()
    expected = [
        Option("LORD", Card.LORD), Option("BANDIT", Card.BANDIT)
    ]

    assert expected == cardlist

def test_return_card(player, deck, state_obs):
    player.return_card(Card.BANDIT) 

    assert Card.BANDIT in deck.cards
    assert Card.BANDIT not in player.cards
    assert 1 == len(player.cards)
    state_obs.notify_return_card.assert_called_once_with(player, Card.BANDIT)

    with pytest.raises(ValueError):
        player.return_card(Card.DIPLOMAT)

def test_lose_life(player, state_obs):
    player.lose_life(Card.BANDIT)

    assert Card.BANDIT not in player.cards
    assert 1 == len(player.cards)

    state_obs.notify_lose_life.assert_called_once_with(player)

def test_choose_action(player, ui, action_obs):
    from depose.actions import Salary
    test_cases = [
        (2, [Option("Salary", "SALARY"), Option("Donations", "DONATIONS"), Option("Tithe", "TITHE"), Option("Mug", "MUG"), Option("Diplomacy", "DIPLOMACY")]),
        (6, [Option("Salary", "SALARY"), Option("Donations", "DONATIONS"), Option("Tithe", "TITHE"), Option("Mug", "MUG"), Option("Diplomacy", "DIPLOMACY"), Option("Murder", "MURDER")]),
        (9, [Option("Salary", "SALARY"), Option("Donations", "DONATIONS"), Option("Tithe", "TITHE"), Option("Mug", "MUG"), Option("Diplomacy", "DIPLOMACY"), Option("Murder", "MURDER"), Option("Depose", "DEPOSE")]),
        (11, [Option("Depose", "DEPOSE")])
    ]
    
    ui.set_state = MagicMock()

    for coins, options in test_cases:
        player.coins = coins
        player.choose_action()
        
        optionlist = ui.set_state.call_args[0][0]
        assert options == optionlist.options

    player.handle("SALARY")
    chosen_action = action_obs.receive_action.call_args[0][0]
    assert "Salary" == chosen_action.name
    assert player == chosen_action.actor


def test_choose_target(player, deck, ui, action_factory):
    target_obs = MagicMock()
    player.add_target_observer(target_obs)
    ui.set_state = MagicMock()

    filler = Player("Target1", deck, action_factory, ui)
    filler.draw_cards(1)
    target = Player("Target2", deck, action_factory, ui)
    target.draw_cards(1)
    expected = [ Option("Target1", filler), Option("Target2", target) ]

    player.player_list = [ filler, player, target]
    player.choose_target()

    optionlist = ui.set_state.call_args[0][0]
    assert expected == optionlist.options

    player.handle(target)
    target_obs.receive_target.assert_called_once_with(target)

def test_receive_response(player, action_obs):
    player.receive_response(True)
    action_obs.receive_accept.assert_called_once_with(player)

    player.receive_response(False)
    action_obs.receive_decline.assert_called_once_with(player)