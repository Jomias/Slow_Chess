from prettytable import PrettyTable, ALL
from constants import *
from numba.experimental import jitclass


position_type = [
    ("bit_boards", nb.uint64[:, :]),
    ("occupancies", nb.uint64[:]),
    ("side", nb.uint8),
    ("en_passant", nb.uint8),
    ("castle", nb.uint8),
    ("hash_key", nb.uint64),
    ("state", nb.uint8),
    ("repetition_dict", nb.types.DictType(nb.uint64, nb.types.int64)),
    ("fifty_moves_count", nb.int64)
]


@jitclass(position_type)
class Position:
    def __init__(self):
        self.bit_boards = np.zeros((2, 6), dtype=np.uint64)
        self.occupancies = np.zeros(3, dtype=np.uint64)
        self.side = WHITE
        self.en_passant = no_sq
        self.castle = no_sq
        self.hash_key = nb.uint64(0)
        self.state = NORMAL
        self.repetition_dict = nb.typed.Dict.empty(
            key_type=nb.uint64,
            value_type=nb.types.int64
        )
        self.fifty_moves_count = 0


@njit(nb.uint64(Position.class_type.instance_type))
def generate_hash_key(pos: Position):
    final_key = 0
    for color in range(2):
        for piece in range(6):
            bb = pos.bit_boards[color][piece]
            while bb:
                sq = get_lsb_index(bb)
                final_key ^= piece_keys[color][piece][sq]
                bb = pop_bit(bb, sq)
    final_key ^= en_passant_keys[pos.en_passant] ^ castle_keys[pos.castle]
    if pos.side == BLACK:
        final_key ^= side_key
    return final_key


def print_board(cur_pos, details=True):
    print()
    cur_board = PrettyTable()
    cur_board.header = False
    cur_board.hrules = ALL
    for rank in range(8):
        row_output = []
        for file in range(8):
            square = rank * 8 + file
            piece = -1
            for i in range(2):
                for j in range(6):
                    if get_bit(cur_pos.bit_boards[i][j], square):
                        piece = 6 * i + j
            if piece != -1:
                row_output.append(ascii_pieces[piece])
            else:
                row_output.append('')
        cur_board.add_row(row_output + [8 - rank])
    cur_board.add_row([f"{col}" for col in 'ABCDEFGH '])
    print(cur_board)
    if details:
        print("Side: " + ("white" if cur_pos.side == WHITE else "black"))
        print("Enpassant: " + (square_to_coordinates[cur_pos.en_passant] if cur_pos.en_passant != no_sq else "no"))
        casl = (
            f"{'K' if cur_pos.castle & wk else ''}{'Q' if cur_pos.castle & wq else ''}"
            f"{'k' if cur_pos.castle & bk else ''}{'q' if cur_pos.castle & bq else ''} "
        )
        print("Castling:", casl if casl else "-")
