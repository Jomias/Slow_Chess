from controllers.game import GameController
from views import *



class MainController:
    def __init__(self):
        pygame.init()
        game = GameController()
        cur_menu = MainMenu(game)
        cur_menu.main_loop()
