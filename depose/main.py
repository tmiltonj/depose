from depose.model import Deck, Card
from depose.player import Player
from depose.actions import ActionFactory
#from depose.game import Game
from depose.view import GUI, IdleState

def main():
    af = ActionFactory()
    deck = create_deck()
    players = create_players(num_players=4, deck=deck)
    
    ui = GUI(players=players)
    ui.set_state(
        IdleState(context=ui, message="Waiting...")
    )

    g = Game(ui=ui, action_factory=af)
    for p in players:
        g.add_player(p)

    g.setup_game()
    g.play()

    ui.mainloop()
    ui.destroy()

def create_deck(num_sets=3):
    deck = Deck()
    for _ in range(num_sets):
        deck.add(Card.LORD)
        deck.add(Card.BANDIT)
        deck.add(Card.MERCENARY)
        deck.add(Card.MEDIC)
        deck.add(Card.DIPLOMAT)

    return deck

def create_players(num_players, game=None, deck=None):
    import random
    names = ["Shinji", "Rei", "Asuka", "Misato", "Gendo", "Kaworu"]
    random.shuffle(names)

    players = []
    for i in range(num_players):
        p = Player(names[i], deck=deck)
        players.append(p)
    return players

if __name__ == "__main__":
    main()