import pygame_menu
import pygame
from pygame_menu import themes
from constants import *


class MainMenu:
    def __init__(self, game_controller):
        self.level = pygame_menu.Menu('Select Settings', GAME_WIDTH, GAME_HEIGHT, theme=themes.THEME_BLUE)
        self.level.add.selector('Difficulty :', [('Easy', 0), ('Medium', 1), ('Hard', 2)], onchange=self.set_difficulty)
        self.level.add.selector('Color :', [('White', 0), ('Black', 1)], onchange=self.set_color)
        self.main_menu = pygame_menu.Menu('Welcome', GAME_WIDTH, GAME_HEIGHT, theme=themes.THEME_GREEN)
        self.main_menu.add.button('Play Computer', self.start_computer_mode)
        self.main_menu.add.button('2 Players', self.start_user_mode)
        self.main_menu.add.button('Setting', self.level_menu)
        self.main_menu.add.button('Quit', pygame_menu.events.EXIT)
        self.controller = game_controller

    def set_difficulty(self, value, difficulty):
        self.controller.difficulty = difficulty

    def set_color(self, value, color):
        self.controller.user_color = color

    def start_user_mode(self):
        self.controller.game_type = USER
        self.controller.play()

    def start_computer_mode(self):
        self.controller.game_type = COMPUTER
        self.controller.play()

    def level_menu(self):
        self.main_menu._open(self.level)


    def main_loop(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    exit()
            if self.main_menu.is_enabled():
                self.main_menu.update(events)
                self.main_menu.draw(self.controller.screen)
                if self.main_menu.get_current().get_selected_widget():
                    self.main_menu.draw(self.controller.screen)
            pygame.display.update()
