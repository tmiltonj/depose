from tkinter import *
from functools import partial

def rgb(r, g, b):
    """ Convert rgb -> hex string """
    return "#%02x%02x%02x" % (r, g, b)


class GUI():
    def __init__(self):
        master = Tk()
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)
        self.master = master

        frame = Frame(master)
        frame.grid(sticky=W+E+N+S)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=0, minsize=120)
        frame.grid_columnconfigure(0, weight=1, minsize=440)
        frame.grid_columnconfigure(1, weight=0)
        self.frame = frame

        self.text = Text(self.frame, state=DISABLED, width=50)
        self.text.grid(row=0, column=0, sticky=W+E+N+S)

        self.dynamic_frame = None
        self.get_frame()

        #self.set_state(IdleState(self, ""))

        self.obs = []

    def attach_player_panel(self, players):
        self.player_panel = PlayerPanel(self.frame, players)
        self.player_panel.frame.grid(row=0, column=1, sticky=W+E+N+S, ipadx=70, rowspan=2)

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

    def get_frame(self):
        if self.dynamic_frame:
            return self.dynamic_frame
        else:
            self.dynamic_frame = Frame(self.frame, height=60)
            self.dynamic_frame.grid(row=1, column=0)
            self.dynamic_frame.grid_rowconfigure(0, weight=1)
            self.dynamic_frame.grid_rowconfigure(1, weight=1)
            self.dynamic_frame.grid_rowconfigure(2, weight=1)

            return self.dynamic_frame
    
    def message(self, text):
        self.text.config(state=NORMAL)
        self.text.insert(END, text)
        self.text.insert(END, '\n')
        self.text.config(state=DISABLED)

    def add_observer(self, obs):
        self.obs.append(obs)

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
                text=option,
                command=partial(self.context.notify, option), # partial() allows us to pass an argument to the callback
                width=int(40 / NUM_COLS)
            )
            buttons.append(b)
            frame.grid_columnconfigure(col, weight=1)
            b.grid(row=1 + int(col / NUM_COLS), column=(col % NUM_COLS), sticky=W+E+N+S, pady=5)


class PlayerPanel():
    MAX_PLAYERS = 6
    IDLE_COLOUR = rgb(210, 210, 220)
    ACTIVE_COLOUR = rgb(200, 250, 200)
    DEAD_COLOUR = rgb(150, 150, 150)
    
    def __init__(self, master, players):
        self.players = players
        self.active_player = 0
        self.panels = []

        self.frame = Frame(master)
        self.frame.grid_columnconfigure(0, weight=1)

        for i in range(self.MAX_PLAYERS):
            self.panels.append(Frame(
                self.frame, 
                background=(self.IDLE_COLOUR if i < len(players) else self.DEAD_COLOUR),
                borderwidth=2, relief=SUNKEN
            ))

            self.frame.grid_rowconfigure(i, weight=1)
            self.panels[i].grid(row=i, sticky=W+E+N+S)

    def set_active(self, index):
        self.panels[self.active_player].config(
            background=self.IDLE_COLOUR
        )

        self.panels[index].config(
            background=self.ACTIVE_COLOUR
        )

        self.active_player = index
        self.update()

    def update(self):
        for panel, player in zip(self.panels, self.players):
            bg = panel.cget('background')
            Label(panel, bg=bg, text="Card A").grid(row=0, column=0)
            Label(panel, bg=bg, text="Card B").grid(row=1, column=0)
            Label(panel, bg=bg, text=player.name).grid(row=0, column=1)
            Label(panel, bg=bg, text="Coins: {}".format(player.coins)).grid(row=1, column=1)

            panel.grid_rowconfigure(0, weight=1)
            panel.grid_rowconfigure(1, weight=1)
            panel.grid_columnconfigure(0, weight=1)
            panel.grid_columnconfigure(1, weight=1)

