import pygame
from src.models.moves.move import *


class Sound:
    def __init__(self):
        self.move = pygame.mixer.Sound("assets/sounds/move-self.mp3")
        self.capture = pygame.mixer.Sound("assets/sounds/capture.mp3")
        self.promote = pygame.mixer.Sound("assets/sounds/promote.mp3")
        self.castle = pygame.mixer.Sound("assets/sounds/castle.mp3")
        self.game_end = pygame.mixer.Sound("assets/sounds/game-end.mp3")
        self.move_check = pygame.mixer.Sound("assets/sounds/move-check.mp3")

    def play_sound(self, m, is_king_in_check):
        if is_king_in_check:
            pygame.mixer.Sound.play(self.move_check)
        elif m.promote_to:
            pygame.mixer.Sound.play(self.promote)
        elif m.capture:
            pygame.mixer.Sound.play(self.capture)
        elif m.castling:
            pygame.mixer.Sound.play(self.castle)
        else:
            pygame.mixer.Sound.play(self.move)


    def play_end(self):
        pygame.mixer.Sound.play(self.game_end)