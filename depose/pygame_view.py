import pygame

pygame.init()

class Card:
    width = 50
    height = 80

    def __init__(self):
        self.color = (255, 255, 255)

    def draw(self, surface, x, y):
        surface.fill(self.color, pygame.Rect(x, y, Card.width, Card.height))

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

# Colours
black = (0, 0, 0)
table_bg = (40, 57, 42)
action_bg = (192, 190, 177)
sidebar_bg = (136, 110, 90)

player_cards = [Card(), Card()]

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

    player_cards[0].draw(table, 10, 10)
    player_cards[1].draw(table, 70, 10)

    # Draw views to main canvas
    screen.blit(table, (0, 0))
    screen.blit(action, (0, 450))
    screen.blit(sidebar, (600, 0))

    # Show display
    pygame.display.flip()