from models.board.position import Position
from constants import *


@njit(nb.uint64(nb.uint, nb.uint8), cache=True)
def mask_pawn_attacks(color, square):
    bb, attacks = set_bit(EMPTY, square), 0
    if color == WHITE:
        attacks |= (bb >> 7) & ~FILES[a]
        attacks |= (bb >> 9) & ~FILES[h]
    if color == BLACK:
        attacks |= (bb << 7) & ~FILES[h]
        attacks |= (bb << 9) & ~FILES[a]
    return attacks


@njit(nb.uint64(nb.uint), cache=True)
def mask_knight_attacks(square):
    bb = set_bit(EMPTY, square)
    return (((bb & ~(FILES[a] | FILES[b])) << 6) | ((bb & ~FILES[a]) << 15) | ((bb & ~FILES[h]) << 17) |
            ((bb & ~(FILES[h] | FILES[g])) << 10) | ((bb & ~(FILES[h] | FILES[g])) >> 6) | ((bb & ~FILES[h]) >> 15) |
            ((bb & ~FILES[a]) >> 17) | ((bb & ~(FILES[a] | FILES[b])) >> 10))


@njit(nb.uint64(nb.uint), cache=True)
def mask_king_attacks(square):
    bb = set_bit(EMPTY, square)
    return (((bb & ~FILES[a]) << 7) | (bb << 8) | ((bb & ~FILES[h]) << 9) | ((bb & ~FILES[h]) << 1) |
            ((bb & ~FILES[h]) >> 7) | (bb >> 8) | ((bb & ~FILES[a]) >> 9) | ((bb & ~FILES[a]) >> 1))


@njit(nb.uint64(nb.uint8), cache=True)
def mask_bishop_attacks(square):
    tr, tf = divmod(square, 8)
    attacks = 0
    directions = np.array([(1, 1), (-1, 1), (1, -1), (-1, -1)])
    for dr, df in directions:
        rank, file = tr + dr, tf + df
        while 0 < rank < 7 and 0 < file < 7:
            attacks |= BIT << (rank * 8 + file)
            rank, file = rank + dr, file + df
    return attacks


@njit(nb.uint64(nb.uint8), cache=True)
def mask_rook_attacks(square):
    attacks = 0
    tr, tf = divmod(square, 8)
    for rank in range(tr + 1, 7):
        attacks |= BIT << (rank * 8 + tf)
    for rank in range(tr - 1, 0, -1):
        attacks |= BIT << (rank * 8 + tf)
    for file in range(tf + 1, 7):
        attacks |= BIT << (tr * 8 + file)
    for file in range(tf - 1, 0, -1):
        attacks |= BIT << (tr * 8 + file)
    return attacks


@njit(nb.uint64(nb.uint8, nb.uint64), cache=True)
def bishop_attacks_on_the_fly(square, block):
    attacks = 0
    tr, tf = divmod(square, 8)
    directions = np.array([(1, 1), (-1, 1), (1, -1), (-1, -1)])
    for direction in directions:
        for reach in range(1, 8):
            rank, file = tr + direction[0] * reach,  tf + direction[1] * reach
            if not 0 <= rank <= 7 or not 0 <= file <= 7:
                break
            attacked_bit = BIT << (rank * 8 + file)
            attacks |= attacked_bit
            if attacked_bit & block:
                break
    return attacks


@njit(nb.uint64(nb.uint8, nb.uint64), cache=True)
def rook_attacks_on_the_fly(square, block):
    attacks = 0
    tr, tf = divmod(square, 8)
    for rank in range(tr + 1, 8):
        attacks |= BIT << (rank * 8 + tf)
        if (1 << (rank * 8 + tf)) & block:
            break
    for rank in range(tr - 1, -1, -1):
        attacks |= BIT << (rank * 8 + tf)
        if BIT << (rank * 8 + tf) & block:
            break
    for file in range(tf + 1, 8):
        attacks |= BIT << (tr * 8 + file)
        if BIT << (tr * 8 + file) & block:
            break
    for file in range(tf - 1, -1, -1):
        attacks |= BIT << (tr * 8 + file)
        if BIT << (tr * 8 + file) & block:
            break
    return attacks


bishop_masks = np.fromiter((mask_bishop_attacks(i) for i in range(64)), dtype=np.uint64)
rook_masks = np.fromiter((mask_rook_attacks(i) for i in range(64)), dtype=np.uint64)


# occ for mgb later
@njit(nb.uint64(nb.uint16, nb.uint8, nb.uint64), cache=True)
def set_occupancy(index, bits_in_mask, attack_mask):
    occupancy = EMPTY
    for count in range(bits_in_mask):
        square = get_lsb_index(attack_mask)
        attack_mask = pop_bit(attack_mask, square)
        if index & (BIT << count):
            occupancy |= BIT << square
    return occupancy


@njit(nb.uint64[:, :](nb.uint64[:, :], nb.b1), cache=True)
def init_sliders(attacks, is_bishop):
    for i in range(64):
        attacks_mask = bishop_masks[i] if is_bishop else rook_masks[i]
        relevant_bits_count = count_bits(attacks_mask)
        occupancy_indices = (1 << relevant_bits_count)
        for index in range(occupancy_indices):
            if is_bishop:
                occupancy = set_occupancy(index, relevant_bits_count, attacks_mask)
                magic_index = (occupancy * bishop_magic_numbers[i]) >> (64 - bishop_relevant_bits[i])
                attacks[i][magic_index] = bishop_attacks_on_the_fly(i, occupancy)
            else:
                occupancy = set_occupancy(index, relevant_bits_count, attacks_mask)
                magic_index = (occupancy * rook_magic_numbers[i]) >> (64 - rook_relevant_bits[i])
                attacks[i][magic_index] = rook_attacks_on_the_fly(i, occupancy)
    return attacks


bishop_attacks = init_sliders(np.empty((64, 512), dtype=np.uint64), is_bishop=True)
rook_attacks = init_sliders(np.empty((64, 4096), dtype=np.uint64), is_bishop=False)
pawn_attacks = np.fromiter((mask_pawn_attacks(color, i) for color in range(2) for i in range(64)), dtype=np.uint64)
pawn_attacks.shape = (2, 64)
knight_attacks = np.fromiter((mask_knight_attacks(i) for i in range(64)), dtype=np.uint64)
king_attacks = np.fromiter((mask_king_attacks(i) for i in range(64)), dtype=np.uint64)


@njit(nb.uint64(nb.uint8, nb.uint64), cache=True)
def get_bishop_attacks(square, occupancy):
    occupancy &= bishop_masks[square]
    occupancy *= bishop_magic_numbers[square]
    occupancy >>= 64 - bishop_relevant_bits[square]
    return bishop_attacks[square][occupancy]


@njit(nb.uint64(nb.uint8, nb.uint64))
def get_rook_attacks(square, occupancy):
    occupancy &= rook_masks[square]
    occupancy *= rook_magic_numbers[square]
    occupancy >>= 64 - rook_relevant_bits[square]
    return rook_attacks[square][occupancy]


@njit(nb.uint64(nb.uint8, nb.uint64))
def get_queen_attacks(square, occupancy):
    return get_rook_attacks(square, occupancy) | get_bishop_attacks(square, occupancy)


@njit(nb.b1(Position.class_type.instance_type, nb.uint8))
def is_square_attacked(cur_pos, square):
    opp = cur_pos.side ^ 1
    if pawn_attacks[cur_pos.side][square] & cur_pos.bit_boards[opp][PAWN] \
            or get_bishop_attacks(square, cur_pos.occupancies[BOTH]) & cur_pos.bit_boards[opp][BISHOP] \
            or knight_attacks[square] & cur_pos.bit_boards[opp][KNIGHT] \
            or get_rook_attacks(square, cur_pos.occupancies[BOTH]) & cur_pos.bit_boards[opp][ROOK] \
            or get_queen_attacks(square, cur_pos.occupancies[BOTH]) & cur_pos.bit_boards[opp][QUEEN] \
            or king_attacks[square] & cur_pos.bit_boards[opp][KING]:
        return True
    return False


@njit
def get_attacks(piece, source, pos):
    if piece == KNIGHT:
        return knight_attacks[source] & ~pos.occupancies[pos.side]
    if piece == BISHOP:
        return get_bishop_attacks(source, pos.occupancies[BOTH]) & ~pos.occupancies[pos.side]
    if piece == ROOK:
        return get_rook_attacks(source, pos.occupancies[BOTH]) & ~pos.occupancies[pos.side]
    if piece == QUEEN:
        return get_queen_attacks(source, pos.occupancies[BOTH]) & ~pos.occupancies[pos.side]
    if piece == KING:
        return king_attacks[source] & ~pos.occupancies[pos.side]
