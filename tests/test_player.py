import pytest
from unittest.mock import Mock, call

from src.depose import Player, Game
from src.model import Deck
from src.view import UI

@pytest.fixture
def player():
    mock_deck = Deck()
    mock_deck.get = Mock(return_value="Card")

    mock_ui = UI()
    mock_ui.get_choice = Mock(side_effect=["A", "B"])

    mock_game = Game(mock_ui)

    return Player(ui=mock_ui, deck=mock_deck, game=mock_game, name="TestPlayer", coins=2)

def test_constructor(player):
    assert "TestPlayer" == player.name
    assert 2 == player.coins

def test_get_action_list(player):
    test_cases = [
        (0, ["Salary", "Donations", "Tithe", "Mug", "Diplomacy"]),
        (3, ["Salary", "Donations", "Tithe", "Mug", "Murder", "Diplomacy"]),
        (7, ["Salary", "Donations", "Tithe", "Depose", "Mug", "Murder", "Diplomacy"]),
        (10, ["Depose"])
    ]

    for amt, expected in test_cases:
        player.coins = amt
        act_list = player._get_action_list()
        assert expected == act_list

def test_lose_life(player):
    player.cards = ["A", "B", "C"]
    player.ui.get_choice = Mock(return_value="A")

    revealed = player.lose_life()
    assert "A" == revealed
    assert 2 == len(player.cards)

    revealed = player.lose_life(card="B")
    assert "B" == revealed
    assert 1 == len(player.cards)

def test_diplomacy(player):
    mock_ui = UI()
    mock_ui.get_choice = Mock(side_effect=["A", "C"])

    mock_deck = Deck()
    mock_deck.get = Mock(side_effect=["C", "D"])
    mock_deck.add = Mock()
    
    player.ui = mock_ui
    player.deck = mock_deck
    player.cards = ["A"]
    pre = len(player.cards)

    player.diplomacy()

    assert pre == len(player.cards)
    assert ["D"] == player.cards
    mock_deck.add.assert_has_calls([call("A"), call("C")])

def test_draw_cards(player):
    test_cases = [
        (-1, 0), (0, 0), (1, 1), (5, 5)
    ]

    for amt, expected in test_cases:
        player.cards = []
        player.draw_cards(amt)
        assert expected == len(player.cards)
