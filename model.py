import random

class Card():
    def __init__(self, name):
        self.name = name

class Deck():
    def __init__(self):
        self.cards = []

    def add(self, card):
        self.cards.append(card)

    def get(self):
        selection = random.choice(self.cards)
        self.cards.remove(selection)
        return selection
            

def main():
    d = Deck()
    d.add(Card("A"))
    d.add(Card("B"))
    d.add(Card("C"))

    print(d.get().name)
    print(d.get().name)
    print(d.get().name)

if __name__ == '__main__':
    main()