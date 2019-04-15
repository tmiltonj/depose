class Event():
    def __init__(self, name, callback):
        self.name = name
        self.callback = callback

    def start(self):
        self.callback()

# Change turn

# Player takes turn
    # Choose action
    # [Choose target]
        # [Choose to call out]
    # [Choose to block]
        # [Choose to call out]
    # Perform action
        # Income
        # FA
        # Coup
        # Tax
        # Steal
        # Assassinate
        # Ambassador

# Player loses coins
# Player loses life
# Player is removed from game

# Name, Callback -> Effect