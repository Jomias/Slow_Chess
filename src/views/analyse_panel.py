from constants import *
import pygame


class Timer:
    def __init__(self, x, y, font_size=24):
        self.x = x
        self.y = y
        self.font_size = font_size
        self.font = pygame.font.Font(None, font_size)
        self.time = 300  # Thời gian ban đầu là 300 giây (5 phút)

    def update(self, elapsed_time):
        self.time -= elapsed_time
        if self.time < 0:
            self.time = 0

    def draw(self, surface):
        timer_text = self.font.render(f"Time: {int(self.time)}", True, WHITE)
        surface.blit(timer_text, (self.x, self.y))


class AnalysePanel:
    def __init__(self):
        self.surface = pygame.Surface((650, 150))
        self.white_timer = Timer(10, 10)
        self.black_timer = Timer(10, 200)

    def update(self, elapsed_time, side):
        if side == WHITE:
            self.white_timer.update(elapsed_time)
        else:
            self.black_timer.update(elapsed_time)


    def show_analyse(self, user_side=WHITE):
        self.surface.fill(BLACK)
        self.white_timer.draw(self.surface)
        self.black_timer.draw(self.surface)

