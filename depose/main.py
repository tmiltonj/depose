from depose.model import Deck, Card
from depose.player import Player
from depose.actions import ActionFactory
from depose.game import Game
#from depose.view import GUI, IdleState

class FakeGUI():
    def set_state(self, state):
        prompt = state.prompt
        options = state.options
        print(">>", prompt)
        for ind, opt in enumerate(options, 1):
            print(">>", ind, opt)

        ind = -1
        while ind <= 0 or ind > len(options):
            try:
                ind = int(input(">> Enter choice: "))
            except ValueError:
                ind = -1

        state.context.handle(options[ind - 1])


def main():
    fake_gui = FakeGUI()
    af = ActionFactory()
    deck = create_deck()

    players = create_players(
        num_players=4, 
        deck=deck,
        action_factory=af,
        ui=fake_gui
    )

    for p in players:
        p.player_list = players
        p.draw_cards(2)
    
    """
    ui = GUI(players=players)
    ui.set_state(
        IdleState(context=ui, message="Waiting...")
    )
    """

    g = Game(players=players, ui=fake_gui)
    g.play()

    """
    ui.mainloop()
    ui.destroy()
    """

def create_deck(num_sets=3):
    deck = Deck()
    for _ in range(num_sets):
        deck.add(Card.LORD)
        deck.add(Card.BANDIT)
        deck.add(Card.MERCENARY)
        deck.add(Card.MEDIC)
        deck.add(Card.DIPLOMAT)

    return deck

def create_players(num_players, deck, action_factory, ui):
    import random
    names = ["Shinji", "Rei", "Asuka", "Misato", "Gendo", "Kaworu"]
    random.shuffle(names)

    players = []
    for name in names[:num_players]:
        p = Player(name, deck=deck, action_factory=action_factory, ui=ui)
        players.append(p)
    return players

if __name__ == "__main__":
    main()