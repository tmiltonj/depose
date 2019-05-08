from tkinter import *
from functools import partial
from collections import namedtuple
from copy import copy

Option = namedtuple('Option', ['label', 'value'])

def rgb(r, g, b):
    """ Convert rgb -> hex string """
    return "#%02x%02x%02x" % (r, g, b)


class GUI():
    def __init__(self):
        master = Tk()
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)
        master.minsize(width=500, height=200)
        self.master = master

        frame = Frame(master)
        frame.grid(sticky=W+E+N+S)
        frame.grid_rowconfigure(0, weight=1, minsize=50)
        frame.grid_rowconfigure(1, weight=0, minsize=120)
        frame.grid_columnconfigure(0, weight=1, minsize=300)
        frame.grid_columnconfigure(1, weight=0)
        frame.grid_columnconfigure(2, weight=1, minsize=180)
        self.frame = frame

        scrollbar = Scrollbar(self.frame)
        scrollbar.grid(row=0, column=1, sticky=W+E+N+S)
        self.text = Text(
            self.frame, 
            state=DISABLED, 
            width=50,
            yscrollcommand=scrollbar.set
        )
        self.text.grid(row=0, column=0, sticky=W+E+N+S)

        scrollbar.config(command=self.text.yview)

        self.dynamic_frame = None
        self.get_frame()

        #self.set_state(IdleState(self, ""))

        self.obs = []

    def attach_player_panel(self, players):
        self.player_panel = PlayerPanel(self.frame, players)
        self.player_panel.frame.grid(row=0, column=2, sticky=W+E+N+S, ipadx=0, rowspan=2)

    def mainloop(self):
        self.master.mainloop()

    def destroy(self):
        self.master.destroy()

    def _clear_view(self):
        if self.dynamic_frame:
            self.dynamic_frame.destroy()
            self.dynamic_frame = None

    def set_state(self, state):
        self._clear_view()
        self.player_panel.update()
        self.state = state
        self.state.update_view()

    def update_active_player(self, player):
        self.player_panel.set_active(player)

    def get_frame(self):
        if self.dynamic_frame:
            return self.dynamic_frame
        else:
            self.dynamic_frame = Frame(self.frame, height=60)
            self.dynamic_frame.grid(row=1, column=0, columnspan=2)
            self.dynamic_frame.grid_rowconfigure(0, weight=1)
            self.dynamic_frame.grid_rowconfigure(1, weight=1)
            self.dynamic_frame.grid_rowconfigure(2, weight=1)

            return self.dynamic_frame
    
    def message(self, text):
        self.text.config(state=NORMAL)
        self.text.insert(END, text)
        self.text.insert(END, '\n')
        self.text.config(state=DISABLED)
        self.text.see(END)

    def add_observer(self, obs):
        print("GUI: Adding", getattr(obs, "name", obs.__class__), "as an obs")
        if obs not in self.obs:
            self.obs.append(obs)

    def remove_observer(self, obs):
        print("GUI: Removing", getattr(obs, "name", obs.__class__), "as an obs")
        if obs in self.obs:
            self.obs.remove(obs)

    def notify(self, event):
        for o in self.obs:
            o.handle(event)


class GUIState():
    def __init__(self, context):
        self.context = context

class IdleState(GUIState):
    def __init__(self, context, message):
        super().__init__(context)
        self.message = message

    def update_view(self):
        frame = self.context.get_frame()
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        Label(frame, text=self.message).grid()

class OptionListState(GUIState):
    def __init__(self, context, prompt, options):
        super().__init__(context)
        self.prompt = prompt
        self.options= options

    def update_view(self):
        NUM_COLS = 4

        frame = self.context.get_frame()
        Label(frame, text=self.prompt).grid(row=0, columnspan=NUM_COLS, sticky=W+E+N+S)
        buttons = []
        for col, option in enumerate(self.options):
            b = Button(
                frame, 
                text=option.label,
                command=partial(self.context.notify, option.value), # partial() allows us to pass an argument to the callback
                width=int(40 / NUM_COLS)
            )
            buttons.append(b)
            frame.grid_columnconfigure(col, weight=1)
            b.grid(row=1 + int(col / NUM_COLS), column=(col % NUM_COLS), sticky=W+E+N+S, pady=5)


class PlayerBox():
    IDLE_COLOUR = rgb(210, 210, 220)
    ACTIVE_COLOUR = rgb(200, 250, 200)
    FOCUS_COLOUR = rgb(200, 200, 230)
    DEAD_COLOUR = rgb(150, 150, 150)
    LABEL_WIDTH = 10

    def __init__(self, master, player):
        self.player = player

        self._box = Frame(
            master,
            background=self.IDLE_COLOUR,
            borderwidth=2, relief=SUNKEN,
        )
        self._box.grid_rowconfigure(0, weight=1)
        self._box.grid_rowconfigure(1, weight=1)
        self._box.grid_columnconfigure(0, weight=1)
        self._box.grid_columnconfigure(1, weight=1)

        self.card_a = Label(self.box, width=self.LABEL_WIDTH, bg=self.IDLE_COLOUR)
        self.card_b = Label(self.box, width=self.LABEL_WIDTH, bg=self.IDLE_COLOUR)
        self.name_label = Label(self.box, text=self.player.name, width=self.LABEL_WIDTH, bg=self.IDLE_COLOUR)
        self.coin_label = Label(self.box, width=self.LABEL_WIDTH, bg=self.IDLE_COLOUR)

        self.labels = [self.card_a, self.card_b, self.name_label, self.coin_label]
        self.update()

        self.card_a.grid(row=0, column=0)
        self.card_b.grid(row=1, column=0)
        self.name_label.grid(row=0, column=1)
        self.coin_label.grid(row=1, column=1)

    @property
    def box(self):
        return self._box

    def update(self, myturn=False, focused=False):
        self.set_bg_color(self.IDLE_COLOUR)
        self.card_a.config(text="")
        self.card_b.config(text="")

        if len(self.player.cards) == 0:
            self.set_bg_color(self.DEAD_COLOUR)
        else:
            if len(self.player.cards) >= 1:
                self.card_a.config(text=self.player.cards[0].name)
            if len(self.player.cards) >= 2:
                self.card_b.config(text=self.player.cards[1].name)

        self.coin_label.config(text="Coins: {}".format(self.player.coins))

        if focused == True:
            self.set_bg_color(self.FOCUS_COLOUR)
            for label in self.labels:
                label.config(borderwidth=4, relief=RAISED)
        else:
            for label in self.labels:
                label.config(borderwidth=2, relief=FLAT)

        if myturn == True:
            self.set_bg_color(self.ACTIVE_COLOUR)

    def set_bg_color(self, color):
        for label in self.labels:
            label.config(bg=color)

        self.box.config(bg=color)


class PlayerPanel():
    MAX_PLAYERS = 6

    def __init__(self, master, players):
        self.frame = Frame(master)
        self.frame.grid_columnconfigure(0, weight=1)

        self.player_boxes = []
        for row, p in enumerate(players):
            player_box = PlayerBox(self.frame, p)
            self.player_boxes.append(player_box)

            self.frame.grid_rowconfigure(row, weight=1)
            player_box.box.grid(row=row, column=0, ipadx=0, sticky=W+E+N+S)

        self.active_player = None

    def set_active(self, player):
        self.active_player = player
        self.update()

    def update(self):
        for box in self.player_boxes:
            is_active = box.player == self.active_player
            box.update(myturn=is_active)
 