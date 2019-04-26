import pytest
from unittest.mock import Mock

from depose.model import Player, Deck, Card
from depose.actions import (
    Result, Actions, ActionFactory, 
    Salary, Donations, Tithe, Depose, Mug, Murder, Diplomacy,
    Targeted, Counterable, Questionable,
)

@pytest.fixture
def deck():
    d = Deck()
    d.add(Card.LORD)
    d.add(Card.BANDIT)
    return d

@pytest.fixture
def player(deck):
    p = Player("Test Player", deck=deck)
    p.coins = 2
    p.add_card(Card.MEDIC)
    p.add_card(Card.MERCENARY)
    return p

@pytest.fixture
def target(deck):
    p = Player("Test Target", deck=deck)
    p.coins = 3
    p.add_card(Card.BANDIT)
    p.add_card(Card.MEDIC)
    return p


@pytest.fixture
def action_factory(player):
    af = ActionFactory()
    return af

def test_actionfactory(action_factory, player):
    for action in Actions:
        action_factory.create(action, player)

    a = action_factory.create(Actions.SALARY, player)
    assert a.name == Salary.name
    a = action_factory.create(Actions.DONATIONS, player)
    assert a.name == Donations.name
    a = action_factory.create(Actions.TITHE, player)
    assert a.name == Tithe.name
    a = action_factory.create(Actions.DEPOSE, player)
    assert a.name == Depose.name
    a = action_factory.create(Actions.MUG, player)
    assert a.name == Mug.name
    a = action_factory.create(Actions.MURDER, player)
    assert a.name == Murder.name
    a = action_factory.create(Actions.DIPLOMACY, player)
    assert a.name == Diplomacy.name


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

def test_depose(player):
    a = Depose(actor=player)
    player.lose_life = Mock()
    a.perform(target=player)
    player.lose_life.assert_called_once()
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

def test_diplomacy(player, deck):
    deck.get = Mock(return_value=Card.BANDIT)
    deck.add = Mock()
    player._choose_card = Mock(side_effect=[Card.MERCENARY, Card.BANDIT])
    a = Diplomacy(actor=player)

    a.perform()
    assert 2 == deck.get.call_count
    assert 2 == deck.add.call_count
    assert 2 == len(player.cards)


""" Test Modifiers """
@pytest.fixture
def action(player):
    a = Mug(actor=player)
    return a

@pytest.fixture
def game():
    g = Mock()
    g.ask_for_challenges = Mock()
    g.ask_for_counters = Mock()
    g.resolve_challenge = Mock()
    return g

def test_targeted(action, player, target):
    player.choose_target = Mock(return_value=target)
    a = Targeted(action)
    a.perform()

    player.choose_target.assert_called_once()
    assert 1 == target.coins
    assert 4 == player.coins

def test_counterable(player, action, target, game):
    a = Counterable(action)
    mock_counter = Mock()
    a.get_counter_action = Mock(return_value=mock_counter)

    game.ask_for_counters.return_value = None
    a.perform(target=target, game=game)
    assert 1 == target.coins
    assert 4 == player.coins

    game.ask_for_counters.return_value = target
    mock_counter.perform = Mock(return_value=Result.FAILURE)
    assert Result.SUCCESS == a.perform(target=target, game=game), "Counter failed -> perform action"

    mock_counter.perform = Mock(return_value=Result.SUCCESS)
    assert Result.FAILURE == a.perform(target=target, game=game), "Counter succeeded -> don't perform action"

    with pytest.raises(ValueError):
        a.perform()

def test_questionable(player, action, target, game):
    player.lose_life = Mock()
    target.lose_life = Mock()
    a = Questionable(action)

    game.ask_for_challenges.return_value = None
    assert Result.SUCCESS == a.perform(target=target, game=game)
    assert 1 == target.coins
    assert 4 == player.coins

    game.ask_for_challenges.return_value = target
    game.resolve_challenge.return_value = Result.CHALLENGE_SUCCESS
    assert Result.FAILURE == a.perform(target=target, game=game)
    #player.lose_life.assert_called_once()

    game.resolve_challenge.return_value = Result.CHALLENGE_FAILURE
    assert Result.SUCCESS == a.perform(target=target, game=game)
    #target.lose_life.assert_called_once()

    with pytest.raises(ValueError):
        a.perform()