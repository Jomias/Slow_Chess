from models import *
from .analyse_panel import *
from .board_panel import *


class GUI:

    def __init__(self, screen):
        self.screen = screen
        self.board_panel = BoardPanel(screen)
        self.analyse_panel = AnalysePanel(screen)


    def draw_game(self, display_board, selected_square=None, user_side=WHITE):
        self.screen.fill(0)
        self.board_panel.show_board_panel(display_board, selected_square, user_side)
