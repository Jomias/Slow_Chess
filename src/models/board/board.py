from models.board.fen import *
from models.moves.move_gen import is_king_in_check, generate_legal_moves


class DisplayBoard:
    def __init__(self):
        self.pos = parse_fen(INIT_POSITION)
        self.ui_board = [[None for _ in range(8)] for _ in range(8)]
        self.last_move = None
        self.moves = {}
        self.update_board()


    def reset_board(self):
        self.pos = parse_fen(INIT_POSITION)
        self.last_move = None
        self.update_board()

    def update_board(self):
        self.moves = {}
        self.ui_board = [[None for _ in range(8)] for _ in range(8)]
        moves_list = generate_legal_moves(self.pos)
        for cur_move in moves_list:
            source = cur_move.source
            target = cur_move.target
            if source not in self.moves.keys():
                self.moves[source] = {}
            self.moves[source][target] = cur_move
        for color in range(2):
            for piece in range(PAWN, KING + 1):
                piece_list = self.pos.bit_boards[color][piece]
                while piece_list:
                    p = get_lsb_index(piece_list)
                    row, col = convert_index_to_row_col(p)
                    self.ui_board[row][col] = (color, piece, False)
                    if color == int(self.pos.side) and piece == KING:
                        self.ui_board[row][col] = (color, piece, is_king_in_check(self.pos))
                    piece_list = pop_bit(piece_list, p)
        if len(self.moves) == 0 and self.pos.state == NORMAL:
            self.pos.state = CHECKMATE if is_king_in_check(self.pos) else STALEMATE
#
# if __name__ == "__main__":
#     a = DisplayBoard()
#     uci_perf(a.pos, 3)
