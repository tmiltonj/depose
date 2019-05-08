import pytest
from depose.model import Deck

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
