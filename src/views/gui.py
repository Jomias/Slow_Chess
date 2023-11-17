import pygame.time

from models import *
from .analyse_panel import *
from .board_panel import *


class GUI:

    def __init__(self, screen):
        self.screen = screen
        self.board_panel = BoardPanel(screen)
        self.analyse_panel = AnalysePanel()


    def draw_game(self, display_board, selected_square=None, user_side=WHITE):
        self.screen.fill(0)
        self.board_panel.show_board_panel(display_board, selected_square, user_side)


    def draw_timer(self, user_side=WHITE):
        self.analyse_panel.show_analyse(user_side=user_side)
        self.screen.blit(self.analyse_panel.surface, (660, 150))