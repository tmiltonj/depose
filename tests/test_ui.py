import pytest
from unittest.mock import Mock, patch

from src.view import UI

@pytest.fixture
def ui():
    return UI()

def test_message(ui, capsys):
    ui.message("Hello world!")
    captured = capsys.readouterr()
    assert "Hello world!\n" == captured.out

def test_error(ui, capsys):
    ui.error("Oh no")
    captured = capsys.readouterr()
    assert "ERROR: Oh no\n" == captured.out

def test_get_integer(ui):
    with patch("builtins.input", side_effect=["a", "-1", "20", "5"]):
        value = ui.get_integer("Enter a value: ", "Invalid", 5, 15)
        assert 5 == value

def test_get_choice(ui):
    options = ["A", "B", "C", "D"]
    with patch("builtins.input", side_effect=["-1", "5", "2"]):
        choice = ui.get_choice("Pick an option: ", options)
        assert "B" == choice