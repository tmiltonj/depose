from model import *
from events import *
from collections import deque

class Game():
    def __init__(self):
        self.event_queue = deque()
        self.players = []

        self.turn_number = 0
        self.active_player = 0

    def setup(self):
        num_players = 0
        while (num_players <= 0):
            try:
                raw_input = input("Enter number of players: ")
                num_players = int(raw_input)
            except NameError as e:
                print("Enter a number")

        self.players = [Player(self, coins=2) for i in range(num_players)]

    def play(self):
        self.add_event(
            Event("Changing turn", self.next_turn)
        )

        self.add_event(
            Event(
                "Turn " + str(self.turn_number), 
                self.players[self.active_player].start_turn
            )
        )

        while True:
            if (len(self.event_queue) > 0):
                next_event = self.event_queue.popleft()
                print(next_event.name)
                next_event.start()
            else:
                break

        print("event_queue empty. Finished")

    def next_turn(self):
        self.active_player = (self.active_player + 1) % len(self.players)

    def add_event(self, event):
        self.event_queue.append(event)

def main():
    coup = Game()
    coup.setup()
    coup.play()

if __name__ == '__main__':
    main()