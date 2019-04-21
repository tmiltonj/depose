from model import Deck, Card, Player
from game import Game, StartTurnState
from view import GUI

def main():
    deck = create_deck()
    players = create_players(num_players=4, deck=deck)

    gui = GUI(players=players)
    game = Game(players=players, state=StartTurnState(), ui=gui)

    gui.add_observer(game)
    game.update()

    gui.mainloop()
    gui.destroy()

def create_deck(num_sets=3):
    deck = Deck()
    for _ in range(num_sets):
        deck.add(Card.LORD)
        deck.add(Card.BANDIT)
        deck.add(Card.MERCENARY)
        deck.add(Card.MEDIC)
        deck.add(Card.DIPLOMAT)

    return deck

def create_players(num_players, game=None, deck=None, ui=None):
    import random
    names = ["Shinji", "Rei", "Asuka", "Misato", "Gendo", "Kaworu"]
    random.shuffle(names)

    players = []
    for i in range(num_players):
        p = Player(names[i])
        players.append(p)
    return players

if __name__ == "__main__":
    main()