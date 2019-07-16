import pygame
import pygame.freetype
import math

pygame.init()

# Colours
black = (0, 0, 0)
table_bg = (40, 57, 42)
action_bg = (192, 190, 177)
sidebar_bg = (136, 110, 90)

class Card:
    width = 50
    height = 80
    color = (255, 255, 255)

    def draw(surface, x, y):
        surface.fill(Card.color, pygame.Rect(x, y, Card.width, Card.height))

class PlayerCard:
    width = 180
    height = 140
    bg_color = table_bg

    def draw(surface, player, x, y, active=False):
        width = PlayerCard.width
        height = PlayerCard.height
        player_card = pygame.Surface((width, height))
        player_card.fill(PlayerCard.bg_color)

        # Outline
        if active:
            pygame.draw.rect(player_card, (255, 255, 255), pygame.Rect(0, 0, width, height), 1)

        # Cards
        Card.draw(player_card, 10, 10)
        Card.draw(player_card, 70, 10)

        # Coins
        for i in range(12):
            pygame.draw.circle(player_card, (255, 255, 100), (17 + ((i % 7) * 16), 106 + 18 * (i // 7)), 6)

        # Avatar
        pygame.draw.rect(player_card, (255, 255, 255), pygame.Rect(130, 10, 40, 40), 1)

        # Draw player card
        surface.blit(player_card, pygame.Rect(x - width / 2, y - height / 2, width, height))

class Sidebar:
    width = 200
    height = 600
    bg_color = sidebar_bg
    line_length = 25
    max_lines = 28

    class Entry:
        def __init__(self, text, color):
            self.text = text
            self.color = color

    def __init__(self):
        self.entries = []
        self.font = pygame.freetype.Font('Retron2000.ttf', size=14)
        self.font.pad = True

    def log(self, message, color=bg_color):
        line = ''
        for word in message.split(' '):
            print(word)
            if (line == '') or (len(line) + len(word) < Sidebar.line_length):
                line += word + ' '
            else:
                self.entries.append(Sidebar.Entry(line, color))
                line = word + ' '
        self.entries.append(Sidebar.Entry(line, color))

    def draw(self, surface):
        sidebar = pygame.Surface((Sidebar.width, Sidebar.height))
        sidebar.fill(Sidebar.bg_color)
        for line, entry in enumerate(self.entries[-Sidebar.max_lines:]):
            render, _ = self.font.render(entry.text, fgcolor=(255, 255, 255), bgcolor=entry.color)
            sidebar.blit(render, (5, 5 + line * 20))

        surface.blit(sidebar, (0, 0))


# Main canvas
size = width, height = (800, 600)
screen = pygame.display.set_mode(size)

# Views
table_w, table_h = (600, 450)
table = pygame.Surface((table_w, table_h))

action_w, action_h = (600, 150)
action = pygame.Surface((action_w, action_h))

sidebar_w, sidebar_h = (200, 600)
sidebar = pygame.Surface((sidebar_w, sidebar_h))

# Test Sidebar
bar = Sidebar()
bar.log("foo")
bar.log("bar", color=(0, 0, 0))
import random
for i in range(20):
    bar.log("I move my mouth away from the mic to breathe", color=(random.randrange(90, 160), 80, random.randrange(10, 90)))

def draw_player_cards(players, surface, x, y):
    angle = 2 * math.pi / len(players)
    x_dist = 210
    y_dist = 150

    box_w = 170
    box_h = 120

    for ii, player in enumerate(players):
        x_draw = x + x_dist * math.sin(ii * angle)
        y_draw = y + y_dist * math.cos(ii * angle)
        PlayerCard.draw(surface, player, x_draw, y_draw, active=(ii == 4))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear display / views
    screen.fill(black)
    table.fill(table_bg)
    action.fill(action_bg)
    sidebar.fill(sidebar_bg)

    draw_player_cards(['a', 'b', 'c', 'd', 'e', 'f'], table, table_w / 2, table_h / 2)
    bar.draw(sidebar)
    #draw_player_cards(['a', 'b', 'c', 'd', 'e'], table, table_w / 2, table_h / 2)

    # Draw views to main canvas
    screen.blit(table, (0, 0))
    screen.blit(action, (0, 450))
    screen.blit(sidebar, (600, 0))

    # Show display
    pygame.display.flip()