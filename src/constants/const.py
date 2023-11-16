import numba as nb
import numpy as np
from numba import njit


SQUARE_MARK = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h'}
INIT_POSITION = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
GAME_WIDTH = 640  # 1060
GAME_HEIGHT = 640
RECORD_WIDTH = 400
BOARD_WIDTH = 640
BOARD_HEIGHT = 640
ROWS = 8
COLS = 8
SQUARE_SIZE = BOARD_WIDTH // COLS
WHITE_COLOR = (119, 154, 88)
DARK_COLOR = (234, 235, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
LAST_MOVE_COLOR = (171, 214, 248, 127)
EMPTY = np.uint64(0)
BIT = np.uint64(1)
UNIVERSE = np.uint64(0xFFFFFFFFFFFFFFFF)

a, b, c, d, e, f, g, h = range(8)

WHITE, BLACK, BOTH = range(3)
USER, COMPUTER = range(2)
PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING = range(6)
NORMAL, STALEMATE, CHECKMATE, DRAW, RESIGN, INSUFFICIENT_MATERIAL = range(6)
OPENING, END_GAME = np.arange(2, dtype=np.uint8)
EASY, MEDIUM, HARD = range(3)

a8, b8, c8, d8, e8, f8, g8, h8, \
    a7, b7, c7, d7, e7, f7, g7, h7, \
    a6, b6, c6, d6, e6, f6, g6, h6, \
    a5, b5, c5, d5, e5, f5, g5, h5, \
    a4, b4, c4, d4, e4, f4, g4, h4, \
    a3, b3, c3, d3, e3, f3, g3, h3, \
    a2, b2, c2, d2, e2, f2, g2, h2, \
    a1, b1, c1, d1, e1, f1, g1, h1, \
    no_sq = range(65)

square_to_coordinates = (
    "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8",
    "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7",
    "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6",
    "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5",
    "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4",
    "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3",
    "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2",
    "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1",
    "-"
)
center_square = np.array((d3, e3, d5, e5, d4, d4, e4, e4))
a_file, b_file, c_file, d_file, e_file, f_file, g_file, h_file = np.array(
    [0x0101010101010101 << i for i in range(8)], dtype=np.uint64
)
FILES = np.array((a_file, b_file, c_file, d_file, e_file, f_file, g_file, h_file))

rank_8, rank_7, rank_6, rank_5, rank_4, rank_3, rank_2, rank_1 = np.array(
    [0x00000000000000FF << 8 * i for i in range(8)], dtype=np.uint64
)
RANKS = np.array((rank_8, rank_7, rank_6, rank_5, rank_4, rank_3, rank_2, rank_1))

ascii_pieces = "PNBRQKpnbrqk."
unicode_pieces = ("♟", "♞", "♝", "♜", "♛", "♚", "♙", "♘", "♗", "♖", "♕", "♔", " ")
wk, wq, bk, bq = (1 << i for i in range(4))

"""
                           castling   move     in      in
                              right update     binary  decimal

 king & rooks didn't move:     1111 & 1111  =  1111    15

        white king  moved:     1111 & 1100  =  1100    12
  white king's rook moved:     1111 & 1110  =  1110    14
 white queen's rook moved:     1111 & 1101  =  1101    13

         black king moved:     1111 & 0011  =  1011    3
  black king's rook moved:     1111 & 1011  =  1011    11
 black queen's rook moved:     1111 & 0111  =  0111    7

"""
castling_rights = np.array([
    7, 15, 15, 15, 3, 15, 15, 11,
    15, 15, 15, 15, 15, 15, 15, 15,
    15, 15, 15, 15, 15, 15, 15, 15,
    15, 15, 15, 15, 15, 15, 15, 15,
    15, 15, 15, 15, 15, 15, 15, 15,
    15, 15, 15, 15, 15, 15, 15, 15,
    15, 15, 15, 15, 15, 15, 15, 15,
    13, 15, 15, 15, 12, 15, 15, 14
], dtype=np.uint8)

# reverse to calculate black side without setting value to negative
mirror_pst = (
    a1, b1, c1, d1, e1, f1, g1, h1,
    a2, b2, c2, d2, e2, f2, g2, h2,
    a3, b3, c3, d3, e3, f3, g3, h3,
    a4, b4, c4, d4, e4, f4, g4, h4,
    a5, b5, c5, d5, e5, f5, g5, h5,
    a6, b6, c6, d6, e6, f6, g6, h6,
    a7, b7, c7, d7, e7, f7, g7, h7,
    a8, b8, c8, d8, e8, f8, g8, h8,
)

reversed_board = (
    h1, g1, f1, e1, d1, c1, b1, a1,
    h2, g2, f2, e2, d2, c2, b2, a2,
    h3, g3, f3, e3, d3, c3, b3, a3,
    h4, g4, f4, e4, d4, c4, b4, a4,
    h5, g5, f5, e5, d5, c5, b5, a5,
    h6, g6, f6, e6, d6, c6, b6, a6,
    h7, g7, f7, e7, d7, c7, b7, a7,
    h8, g8, f8, e8, d8, c8, b8, a8
)
MAX_PLY = 64

# Capture ordering
# most valuable victim & less valuable attacker
# MVV LVA [attacker][victim]
MVV_LVA = np.array((
    (105, 205, 305, 405, 505, 605),
    (104, 204, 304, 404, 504, 604),
    (103, 203, 303, 403, 503, 603),
    (102, 202, 302, 402, 502, 602),
    (101, 201, 301, 401, 501, 601),
    (100, 200, 300, 400, 500, 600),
))

BOUND_INF = 50000
LOWER_MATE = 48000
UPPER_MATE = 49000

# LMR
full_depth_moves = 4
reduction_limit = 3

# Zobrist hashing
# init random hash keys
# seed_value = 42
# np.random.seed(seed_value)
piece_keys = np.random.randint(2 ** 64 - 1, size=(2, 6, 64), dtype=np.uint64)
en_passant_keys = np.random.randint(2 ** 64 - 1, size=65, dtype=np.uint64)
castle_keys = np.random.randint(2 ** 64 - 1, size=16, dtype=np.uint64)
side_key = np.random.randint(2 ** 64 - 1, dtype=np.uint64)
MAX_HASH_SIZE = 0x400000

# transposition flag
hash_flag_exact, hash_flag_alpha, hash_flag_beta = range(3)
no_hash_entry = 100000

hash_numpy_type = np.dtype(
    [("key", np.uint64),  # unique position
     ("depth", np.uint8),  # current depth
     ("flag", np.uint8),  # fail low, fail high, PV
     ("score", np.int64)]  # alpha, beta, PV
)
hash_numba_type = nb.from_dtype(hash_numpy_type)

time_precision = 2047