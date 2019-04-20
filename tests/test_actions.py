import pytest
from unittest.mock import Mock, patch

from collections import deque

from src.depose import Game, Player
from src.model import Deck, Card
from src.view import UI
from src.actions import *

""" Test basic actions """
@pytest.fixture
def dummy_game():
    ui = UI()
    ui.get_confirm = Mock(return_value=False) # No blocking or calling out
    deck = Deck()
    game = Game(ui=ui)
    
    actor = Player(ui=ui, deck=deck, game=game, name="TestActor")
    target = Player(ui=ui, deck=deck, game=game, name="TestTarget")
    
    game.players = deque([actor, target])

    action_factory = ActionFactory(actor, ui, game)

    return { "game": game, "actor": actor, "target": target, "action_factory": action_factory }

class TestActions():
    def test_salary(self, dummy_game):
        act = dummy_game["action_factory"].salary()
        dummy_game["actor"].coins = 5
        act.do()
        assert 6 == dummy_game["actor"].coins

    def test_donations(self, dummy_game):
        act = dummy_game["action_factory"].donations()
        dummy_game["actor"].coins = 2
        act.do()
        assert 4 == dummy_game["actor"].coins

    def test_tithe(self, dummy_game):
        act = dummy_game["action_factory"].tithe()
        dummy_game["actor"].coins = 9
        act.do()
        assert 12 == dummy_game["actor"].coins

    def test_depose(self, dummy_game):
        act = dummy_game["action_factory"].depose()
        dummy_game["actor"].coins = 10
        dummy_game["target"].cards = ["A"]
        with patch("builtins.input", return_value="1"):
            act.do()
            assert 3 == dummy_game["actor"].coins
            assert 0 == len(dummy_game["target"].cards)

    def test_mug(self, dummy_game):
        act = dummy_game["action_factory"].mug()
        dummy_game["actor"].coins = 1
        dummy_game["target"].coins = 3
        with patch("builtins.input", return_value="1"):
            act.do() # Steal 2 coins
            assert 3 == dummy_game["actor"].coins
            assert 1 == dummy_game["target"].coins
            
            act.do() # Steal 1 coin
            assert 4 == dummy_game["actor"].coins
            assert 0 == dummy_game["target"].coins

            act.do() # Steal 0 coins
            assert 4 == dummy_game["actor"].coins
            assert 0 == dummy_game["target"].coins

    def test_murder(self, dummy_game):
        act = dummy_game["action_factory"].murder()
        dummy_game["actor"].coins = 5
        dummy_game["target"].cards = ["A", "B"]
        with patch("builtins.input", return_value="1"):
            act.do()
            assert 2 == dummy_game["actor"].coins
            assert 1 == len(dummy_game["target"].cards)

    def test_diplomacy(self, dummy_game):
        act = dummy_game["action_factory"].diplomacy()
        dummy_game["actor"].diplomacy = Mock()
        act.do()
        dummy_game["actor"].diplomacy.assert_called_once()


""" Test Decorated Actions """
ACCEPT_BLOCK = 'y'
DECLINE_BLOCK = 'n'
ACCEPT_CALL = 'y'
DECLINE_CALL = 'n'

@pytest.fixture
def dec_game():
    ui = UI()
    deck = Deck()

    game = Game(ui)
    actor = Player(ui, deck, game, name="PlayerA")
    target = Player(ui, deck, game, name="PlayerB")
    bystander = Player(ui, deck, game, name="PlayerC")
    game.players = deque([actor, target, bystander])

    base_action = Action(actor, ui, game)
    base_action.do = Mock()

    return { "game": game, "actor": actor, "target": target, "bystander": bystander, "base_action": base_action }

class TestActionDecorators():
    def test_targeted(self, dec_game):
        base_action = dec_game["base_action"]
        act = Targeted(base_action)

        with patch("builtins.input", return_value="2"):
            act.do()
            base_action.do.assert_called_once_with(dec_game["bystander"])

    def test_blockable(self, dec_game):
        actor, target, bystander = dec_game["actor"], dec_game["target"], dec_game["bystander"]
        base_action = dec_game["base_action"]
        act = Blockable(base_action)
        act.name = "Donations"

        # ACTION NOT BLOCKED
        with patch("builtins.input", return_value=DECLINE_BLOCK):
            # Non targeted 
            act.do()
            base_action.do.assert_called_once()
        
            # Single target
            base_action.do.reset_mock()
            act.do(target=target)
            base_action.do.assert_called_once()

        # ACTION BLOCKED
        # Non targeted 
        base_action.do.reset_mock()
        with patch("builtins.input", side_effect=[DECLINE_BLOCK, ACCEPT_BLOCK, DECLINE_CALL, DECLINE_CALL]):
            act.do()
            base_action.do.assert_not_called()
        
        # Single target
        base_action.do.reset_mock()
        with patch("builtins.input", side_effect=[ACCEPT_BLOCK, DECLINE_CALL, DECLINE_CALL]):
            act.do(target=target)
            base_action.do.assert_not_called()

        # BLOCKED AND CALLED OUT
        # target blocks > bystander calls out (successfully) > target loses life > action is performed
        base_action.do.reset_mock()
        target.lose_life = Mock()
        target.cards = [Card("Bandit")]
        with patch("builtins.input", side_effect=[ACCEPT_BLOCK, DECLINE_CALL, ACCEPT_CALL, "1"]):
            act.do()
            base_action.do.assert_called_once()
            target.lose_life.assert_called_once()
        
        # BLOCKED AND CALLED OUT UNSUCCESSFULLY
        # bystander blocks > actor calls out (fails) > actor loses life > no action occurs
        base_action.do.reset_mock()
        actor.lose_life = Mock()
        bystander.cards = [Card("Lord")]
        with patch("builtins.input", side_effect=[DECLINE_BLOCK, ACCEPT_BLOCK, ACCEPT_CALL, "1"]):
            act.do()
            base_action.do.assert_not_called()
            actor.lose_life.assert_called_once()

    def test_callable(self, dec_game):
        actor, bystander = dec_game["actor"], dec_game["bystander"]
        base_action = dec_game["base_action"]
        act = Callable(base_action)
        act.name = "Tithe"

        # NOT CALLED OUT        
        with patch("builtins.input", return_value=DECLINE_CALL):
            act.do()
            base_action.do.assert_called_once()

        # CALLED OUT (SUCCESSFUL), actor has the card
        base_action.do.reset_mock()
        actor.cards = [Card("Lord")]
        bystander.lose_life = Mock()
        with patch("builtins.input", side_effect=[DECLINE_CALL, ACCEPT_CALL, "1"]):
            act.do()
            base_action.do.assert_called_once()
            bystander.lose_life.assert_called_once()

        # CALLED OUT (FAILED), actor does not have the card
        base_action.do.reset_mock()
        actor.cards = [Card("Bandit")]
        actor.lose_life = Mock()
        with patch("builtins.input", side_effect=[ACCEPT_CALL, "1"]):
            act.do()
            base_action.do.assert_not_called()
            actor.lose_life.assert_called_once()


""" Test ActionFactory """
@pytest.fixture
def action_factory():
    mock_ui = UI()
    mock_deck = Deck()
    mock_game = Game(ui=mock_ui)
    mock_player = Player(ui=mock_ui, deck=mock_deck, game=mock_game)

    return ActionFactory(mock_player, mock_ui, mock_game)

class TestActionFactory():
    def test_salary(self, action_factory):
        act = action_factory.salary()
        assert "Salary" == act.name

    def test_donations(self, action_factory):
        act = action_factory.donations()
        assert "Donations" == act.name
        assert act.__class__ == Blockable
        assert act.action.__class__ == Donations

    def test_tithe(self, action_factory):
        act = action_factory.tithe()
        assert "Tithe" == act.name
        assert act.__class__ == Callable
        assert act.action.__class__ == Tithe

    def test_depose(self, action_factory):
        act = action_factory.depose()
        assert "Depose" == act.name
        assert act.__class__ == Targeted
        assert act.action.__class__ == Depose

    def test_mug(self, action_factory):
        act = action_factory.mug()
        assert "Mug" == act.name
        assert act.__class__ == Targeted
        assert act.action.__class__ == Callable
        assert act.action.action.__class__ == Blockable
        assert act.action.action.action.__class__ == Mug

    def test_murder(self, action_factory):
        act = action_factory.murder()
        assert "Murder" == act.name
        assert act.__class__ == Targeted
        assert act.action.__class__ == Callable
        assert act.action.action.__class__ == Blockable

    def test_diplomacy(self, action_factory):
        act = action_factory.diplomacy()
        assert "Diplomacy" == act.name
        assert act.__class__ == Callable
        assert act.action.__class__ == Diplomacy

    def test_blocking_actions(self, action_factory):
        act = action_factory.block_donations()
        assert "Block Donations" == act.name
        assert act.__class__ == Callable
        assert act.action.__class__ == BlockDonations

        act = action_factory.block_mug()
        assert "Block Mug" == act.name
        assert act.__class__ == Callable
        assert act.action.__class__ == BlockMug

        act = action_factory.block_murder()
        assert "Block Murder" == act.name
        assert act.__class__ == Callable
        assert act.action.__class__ == BlockMurder
