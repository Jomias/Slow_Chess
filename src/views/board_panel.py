import pygame

from constants import *
from models import *


class BoardPanel:

    def __init__(self, screen):
        self.screen = screen
        self.piece_images = \
            {WHITE: {
                PAWN: pygame.image.load('assets/images/80px/wP.png'),
                KNIGHT: pygame.image.load('assets/images/80px/wN.png'),
                BISHOP: pygame.image.load('assets/images/80px/wB.png'),
                ROOK: pygame.image.load('assets/images/80px/wR.png'),
                QUEEN: pygame.image.load('assets/images/80px/wQ.png'),
                KING: pygame.image.load('assets/images/80px/wK.png'),

            }, BLACK: {
                ROOK: pygame.image.load('assets/images/80px/bR.png'),
                KNIGHT: pygame.image.load('assets/images/80px/bN.png'),
                BISHOP: pygame.image.load('assets/images/80px/bB.png'),
                QUEEN: pygame.image.load('assets/images/80px/bQ.png'),
                KING: pygame.image.load('assets/images/80px/bK.png'),
                PAWN: pygame.image.load('assets/images/80px/bP.png'),
            }}

    def show_board_panel(self, display_board: DisplayBoard, selected_square=None, user_side=WHITE):
        for row in range(ROWS):
            for col in range(COLS):
                color = DARK_COLOR if (row + col) % 2 == 0 else WHITE_COLOR
                rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, rect)

        if user_side == WHITE:
            row_labels = [pygame.font.SysFont('arial', 18, bold=True)
                          .render(str(ROWS - row), 1, DARK_COLOR if row % 2 == 1 else WHITE_COLOR) for row in range(ROWS)]
            col_labels = [pygame.font.SysFont('arial', 18, bold=True)
                          .render(SQUARE_MARK[col + 1], 1, DARK_COLOR if col % 2 == 0 else WHITE_COLOR) for col in
                          range(COLS)]
        else:
            row_labels = [pygame.font.SysFont('arial', 18, bold=True)
                          .render(str(1 + row), 1, DARK_COLOR if row % 2 == 1 else WHITE_COLOR) for row in range(ROWS)]
            col_labels = [pygame.font.SysFont('arial', 18, bold=True)
                          .render(SQUARE_MARK[8 - col], 1, DARK_COLOR if col % 2 == 0 else WHITE_COLOR) for col in
                          range(COLS)]
        for row, lbl in enumerate(row_labels):
            self.screen.blit(lbl, (5, 5 + row * SQUARE_SIZE))
        for col, lbl in enumerate(col_labels):
            self.screen.blit(lbl, (col * SQUARE_SIZE + SQUARE_SIZE - 10, GAME_HEIGHT - 21))

        cur_board = display_board.ui_board
        for i in range(8):
            for j in range(8):
                if cur_board[i][j] is not None:
                    _c, p, in_check = cur_board[i][j]
                    if user_side == WHITE:
                        img_center = j * SQUARE_SIZE + SQUARE_SIZE // 2, i * SQUARE_SIZE + SQUARE_SIZE // 2
                        if in_check:
                            pygame.draw.rect(self.screen, RED,
                                             (j * SQUARE_SIZE, i * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 2)
                    else:
                        _i, _j = convert_index_to_row_col(reversed_board[convert_row_col_to_index(i, j)])
                        img_center = _j * SQUARE_SIZE + SQUARE_SIZE // 2, _i * SQUARE_SIZE + SQUARE_SIZE // 2
                        if in_check:
                            pygame.draw.rect(self.screen, RED,
                                             (_j * SQUARE_SIZE, _i * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 2)
                    self.screen.blit(self.piece_images[_c][p], self.piece_images[_c][p].get_rect(center=img_center))

        if selected_square is not None:     # move hint
            row_sq, col_sq = convert_index_to_row_col(selected_square)
            if cur_board[row_sq][col_sq][0] == display_board.pos.side:
                if user_side == BLACK:
                    row_sq, col_sq = convert_index_to_row_col(reversed_board[selected_square])
                pygame.draw.rect(self.screen, GREEN, (col_sq * SQUARE_SIZE, row_sq * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 2)
            for square in display_board.moves.get(selected_square, {}).keys():
                x, y = convert_index_to_row_col(square) if user_side == WHITE else convert_index_to_row_col(reversed_board[square])
                pygame.draw.rect(self.screen, BLUE, (y * SQUARE_SIZE, x * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 2)

        if display_board.last_move is not None:
            source, target = display_board.last_move
            if user_side == BLACK:
                source, target = reversed_board[source], reversed_board[target]
            row_from, col_from = convert_index_to_row_col(source)
            row_to, col_to = convert_index_to_row_col(target)
            target_rect1 = pygame.Rect((col_from * SQUARE_SIZE, row_from * SQUARE_SIZE), (SQUARE_SIZE, SQUARE_SIZE))
            target_rect2 = pygame.Rect((col_to * SQUARE_SIZE, row_to * SQUARE_SIZE), (SQUARE_SIZE, SQUARE_SIZE))
            shape_surface = pygame.Surface(target_rect1.size, pygame.SRCALPHA)
            pygame.draw.rect(shape_surface, LAST_MOVE_COLOR, shape_surface.get_rect())
            self.screen.blit(shape_surface, target_rect1)
            self.screen.blit(shape_surface, target_rect2)


