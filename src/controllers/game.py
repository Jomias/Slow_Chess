import math
import sys
from tkinter import *
from tkinter import messagebox
from src.views import *
from controllers.sound import Sound
from src.models.moves.move_gen import is_king_in_check, random_move


def get_board_pos(pos):
    return math.floor(pos[1] / SQUARE_SIZE) * 8 + math.floor(pos[0] / SQUARE_SIZE)


class GameController:
    def __init__(self):
        self.game_board = DisplayBoard()
        self.ai = Stupid()
        search(self.ai, self.game_board.pos, time_limit=5000)
        self.game_type = USER
        self.is_piece_selected = False
        self.selected_square = None
        self.user_color = WHITE
        self.difficulty = EASY
        self.screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
        pygame.display.set_caption('CHESS GAME')
        self.gui = GUI(self.screen)
        self.sound = Sound()

    def play(self):
        self.game_board.reset_board()
        if self.game_type == USER:
            self.play_user()
        else:
            self.play_computer()

    def play_user(self):
        self.gui.draw_game(self.game_board, self.selected_square)
        pygame.display.update()
        while True:
            if self.game_board.pos.state != NORMAL:
                self.sound.play_end()
                window = Tk()
                window.eval('tk::PlaceWindow %s center' % window.winfo_toplevel())
                window.withdraw()
                window.geometry("500x200")
                if self.game_board.pos.state == DRAW or self.game_board.pos.state == STALEMATE:
                    messagebox.showinfo("Game ended", "Draw !")
                if self.game_board.pos.state == CHECKMATE:
                    if self.game_board.pos.side == WHITE:
                        messagebox.showinfo("Game ended", "Black Win !")
                    else:
                        messagebox.showinfo("Game ended", "White Win !")
                if self.game_board.pos.state == RESIGN:
                    if self.game_board.pos.side == WHITE:
                        messagebox.showinfo("Game ended", "White Resigned! Black Win!")
                    else:
                        messagebox.showinfo("Game ended", "Black Resigned! White Win!")
                window.deiconify()
                window.destroy()
                window.quit()
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.game_board.pos.state = RESIGN
                        break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if pos[0] > BOARD_WIDTH:
                        continue
                    pos = get_board_pos(pos)
                    if self.selected_square is None:
                        _x, _y = convert_index_to_row_col(pos)
                        if self.game_board.ui_board[_x][_y] is not None:
                            self.selected_square = pos
                    else:
                        target = pos
                        if nb.uint64(1 << target) & self.game_board.pos.occupancies[self.game_board.pos.side]:
                            self.selected_square = target
                            continue
                        if self.selected_square in self.game_board.moves and target in self.game_board.moves[self.selected_square]:
                            move = self.game_board.moves[self.selected_square][target]
                            self.game_board.pos = apply_move(self.game_board.pos, move)
                            self.game_board.last_move = (self.selected_square, target)
                            self.game_board.update_board()
                            self.sound.play_sound(move, is_king_in_check(self.game_board.pos))
                        self.selected_square = None
                self.gui.draw_game(self.game_board, self.selected_square)
                pygame.display.update()

    def play_computer(self):
        self.gui.draw_game(self.game_board, self.selected_square, user_side=self.user_color)
        pygame.display.update()
        find_move = self.user_color != WHITE
        while True:
            if self.game_board.pos.state != NORMAL:
                self.sound.play_end()
                window = Tk()
                window.eval('tk::PlaceWindow %s center' % window.winfo_toplevel())
                window.withdraw()
                window.geometry("500x200")
                if self.game_board.pos.state == DRAW or self.game_board.pos.state == STALEMATE:
                    messagebox.showinfo("Game ended", "Draw !")
                if self.game_board.pos.state == CHECKMATE:
                    if self.game_board.pos.side == self.user_color:
                        messagebox.showinfo("Game ended", "You Lose !")
                    else:
                        messagebox.showinfo("Game ended", "You Win !")
                if self.game_board.pos.state == RESIGN:
                    messagebox.showinfo("Game ended", "You Lose !")
                window.deiconify()
                window.destroy()
                window.quit()
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.game_board.pos.state = RESIGN
                        break
                elif self.game_board.pos.side != self.user_color and find_move:
                    if self.difficulty == MEDIUM:
                        search(self.ai, self.game_board.pos, node_limit=2000)
                    elif self.difficulty == HARD:
                        search(self.ai, self.game_board.pos, time_limit=5000)
                    move = random_move(self.game_board.pos) if self.difficulty == EASY else Move(self.ai.pv_table[0][0])
                    self.game_board.pos = apply_move(self.game_board.pos, move)
                    self.game_board.last_move = (move.source, move.target)
                    self.game_board.update_board()
                    self.sound.play_sound(move, is_king_in_check(self.game_board.pos))
                    find_move = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not find_move:
                    pos = pygame.mouse.get_pos()
                    if pos[0] > BOARD_WIDTH:
                        continue
                    pos = get_board_pos(pos)
                    if self.user_color == BLACK:
                        pos = reversed_board[pos]
                    if self.selected_square is None:
                        _x, _y = convert_index_to_row_col(pos)
                        if self.game_board.ui_board[_x][_y] is not None:
                            self.selected_square = pos
                    else:
                        target = pos
                        if nb.uint64(1 << target) & self.game_board.pos.occupancies[self.game_board.pos.side]:
                            self.selected_square = target
                            continue
                        if self.selected_square in self.game_board.moves and target in self.game_board.moves[self.selected_square]:
                            move = self.game_board.moves[self.selected_square][target]
                            self.game_board.pos = apply_move(self.game_board.pos, move)
                            self.game_board.last_move = (self.selected_square, target)
                            self.game_board.update_board()
                            self.sound.play_sound(move, is_king_in_check(self.game_board.pos))
                            find_move = True
                        self.selected_square = None
                self.gui.draw_game(self.game_board, self.selected_square, user_side=self.user_color)
                pygame.display.update()