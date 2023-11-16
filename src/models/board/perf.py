import time

from numba import njit

from models.moves.move_gen import get_move_uci, generate_legal_moves, apply_move


@njit
def compile_perf(_board, depth):
    if depth == 0:
        return 1
    count = 0
    _moves = generate_legal_moves(_board)
    for m in _moves:
        new_board = apply_move(_board, m)
        count += compile_perf(new_board, depth - 1)
    return count


def uci_perf(cur_pos, depth):
    t = time.perf_counter()
    _moves = generate_legal_moves(cur_pos)
    total = 0
    for m in _moves:
        count = 0
        new_board = apply_move(cur_pos, m)
        count += compile_perf(new_board, depth - 1)
        total += count
        print(f"{get_move_uci(m)}: {count}")
    print("\nnodes searched: ", total)
    print(f"perf speed: {total / 1000 / (time.perf_counter() - t):.3f} kn/s")