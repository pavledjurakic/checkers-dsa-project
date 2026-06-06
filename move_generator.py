from board import Board
from piece import Player, PieceType
from square import Square
from relics import *


def get_moves(square: Square, board: Board) -> list:
    """
    Glavna funkcija. Prima polje i tablu.
    Vraca listu validnih poteza za figuru na tom polju.

    Svaki potez je tuple oblika:
        (to_row, to_col, [captured], frozenset(relics_used))

    Primeri:
        (3, 4, [], frozenset())
        (1, 6, [(4,3)], frozenset())
        (1, 2, [(4,3),(2,1)], frozenset({RelicType.TOPUZ}))
    """
    piece = square.piece
    if piece is None:
        return []

    match piece.piece_type:
        case PieceType.JUNAK:
            return get_junak_moves(square, board)
        case PieceType.KRALJEVIC | PieceType.MARKO_KRALJEVIC:
            return get_kraljevic_moves(square, board)

    return []


# ================
# POMOCNE FUNKCIJE
# ================

def is_out_of_bounds(row: int, col: int) -> bool:
    return not (0 <= row <= 7 and 0 <= col <= 7)


# =====
# JUNAK
# =====

def get_junak_moves(square: Square, board: Board) -> list:
    piece    = square.piece
    player   = piece.player
    row_dir  = piece.forward_direction()

    # Hesitation blokira skokove, ali NE Topuz (on je direktan ulazak)
    can_jump = piece.hesitation_turns == 0

    normal_moves = []
    jump_moves   = []

    for col_dir in (+1, -1):
        target_row = square.row + row_dir
        target_col = square.col + col_dir

        if is_out_of_bounds(target_row, target_col):
            continue

        piece_on_target = board.get_piece(target_row, target_col)

        if piece_on_target is None:
            normal_moves.append((target_row, target_col, [], frozenset()))

        elif piece_on_target.player != player and piece_on_target.armor_turns == 0:
            landing_row  = square.row + 2 * row_dir
            landing_col  = square.col + 2 * col_dir
            landing_free = (not is_out_of_bounds(landing_row, landing_col) and
                            board.get_piece(landing_row, landing_col) is None)
            topuz_avail  = RelicType.TOPUZ in piece.active_relics

            if landing_free and can_jump:
                # Normalan skok (sa lancima)
                chains = get_junak_jump_chains(
                    landing_row, landing_col, board, player, row_dir, piece,
                    frozenset({(target_row, target_col)}), frozenset()
                )
                for (fr, fc, caps, rel) in chains:
                    jump_moves.append((fr, fc, [(target_row, target_col)] + caps, rel))

                # Topuz kao ALTERNATIVA: direktan udarac bez obaveze lanca
                # Igrac bira - normalan skok ILI brz udarac Topuzom
                if topuz_avail:
                    jump_moves.append((target_row, target_col,
                                       [(target_row, target_col)],
                                       frozenset({RelicType.TOPUZ})))

            elif topuz_avail:
                # Jedino Topuz moze (sletiste zauzeto ili hesitation blokira skok)
                # Hesitation NE blokira Topuz - direktan ulazak bez preskakanja
                chains = get_junak_jump_chains(
                    target_row, target_col, board, player, row_dir, piece,
                    frozenset({(target_row, target_col)}),
                    frozenset({RelicType.TOPUZ})
                )
                for (fr, fc, caps, rel) in chains:
                    jump_moves.append((fr, fc, [(target_row, target_col)] + caps, rel))

        elif piece_on_target.player == player and can_jump:
            # Sarac: preskoci sopstvenu figuru (jeste skok, blokiran hesitationom)
            sarac_avail = RelicType.SARAC in piece.active_relics
            if sarac_avail:
                landing_row = square.row + 2 * row_dir
                landing_col = square.col + 2 * col_dir
                if (not is_out_of_bounds(landing_row, landing_col) and
                        board.get_piece(landing_row, landing_col) is None):
                    chains = get_junak_jump_chains(
                        landing_row, landing_col, board, player, row_dir, piece,
                        frozenset(), frozenset({RelicType.SARAC})
                    )
                    for (fr, fc, caps, rel) in chains:
                        if caps:
                            jump_moves.append((fr, fc, caps, rel))
                        else:
                            normal_moves.append((fr, fc, [], rel))

    return jump_moves if jump_moves else normal_moves


def get_junak_jump_chains(landing_row: int, landing_col: int, board: Board,
                          player: Player, row_dir: int, piece,
                          already_captured: frozenset, relics_used: frozenset) -> list:
    """
    Rekurzivna funkcija za lancane skokove Junaka.

    piece            -- originalna figura (proveravamo piece.active_relics direktno)
    already_captured -- frozenset koordinata vec pojedenih u ovom lancu
    relics_used      -- frozenset relikvija iskoriscenih u ovom lancu

    Vraca listu (final_row, final_col, [dalje_captured], relics_used).
    """
    # Proveravamo dostupnost direktno iz piece.active_relics minus vec iskoriscene u ovom lancu
    topuz_avail = RelicType.TOPUZ in piece.active_relics and RelicType.TOPUZ not in relics_used
    sarac_avail = RelicType.SARAC in piece.active_relics and RelicType.SARAC not in relics_used

    paths = []

    for col_dir in (+1, -1):
        enemy_row     = landing_row + row_dir
        enemy_col     = landing_col + col_dir
        next_land_row = landing_row + 2 * row_dir
        next_land_col = landing_col + 2 * col_dir

        if is_out_of_bounds(enemy_row, enemy_col):
            continue

        piece_at = board.get_piece(enemy_row, enemy_col)
        if piece_at is None:
            continue

        if (piece_at.player != player and piece_at.armor_turns == 0
                and (enemy_row, enemy_col) not in already_captured):

            next_free = (not is_out_of_bounds(next_land_row, next_land_col) and
                         board.get_piece(next_land_row, next_land_col) is None)

            if next_free:
                # Normalan skok
                sub = get_junak_jump_chains(
                    next_land_row, next_land_col, board, player, row_dir, piece,
                    already_captured | {(enemy_row, enemy_col)}, relics_used
                )
                for (fr, fc, caps, rel) in sub:
                    paths.append((fr, fc, [(enemy_row, enemy_col)] + caps, rel))

            elif topuz_avail:
                # Topuz: uskaci na neprijateljevo polje
                sub = get_junak_jump_chains(
                    enemy_row, enemy_col, board, player, row_dir, piece,
                    already_captured | {(enemy_row, enemy_col)},
                    relics_used | {RelicType.TOPUZ}
                )
                for (fr, fc, caps, rel) in sub:
                    paths.append((fr, fc, [(enemy_row, enemy_col)] + caps, rel))

        elif piece_at.player == player and sarac_avail:
            if (not is_out_of_bounds(next_land_row, next_land_col) and
                    board.get_piece(next_land_row, next_land_col) is None):
                # Sarac unutar lanca
                sub = get_junak_jump_chains(
                    next_land_row, next_land_col, board, player, row_dir, piece,
                    already_captured, relics_used | {RelicType.SARAC}
                )
                for (fr, fc, caps, rel) in sub:
                    paths.append((fr, fc, caps, rel))

    if not paths:
        return [(landing_row, landing_col, [], relics_used)]
    return paths


# ==========================================
# KRALJEVIC  (i MARKO KRALJEVIC — isti su)
# ==========================================

def get_kraljevic_moves(square: Square, board: Board) -> list:
    piece    = square.piece
    player   = piece.player
    can_jump = piece.hesitation_turns == 0

    normal_moves = []
    jump_moves   = []

    for col_direction in (+1, -1):
        for row_direction in (+1, -1):
            target_row = square.row + row_direction
            target_col = square.col + col_direction

            while not is_out_of_bounds(target_row, target_col):
                piece_on_target = board.get_piece(target_row, target_col)

                if piece_on_target is None:
                    normal_moves.append((target_row, target_col, [], frozenset()))

                elif piece_on_target.player != player and piece_on_target.armor_turns == 0:
                    landing_row  = target_row + row_direction
                    landing_col  = target_col + col_direction
                    landing_free = (not is_out_of_bounds(landing_row, landing_col) and
                                    board.get_piece(landing_row, landing_col) is None)
                    topuz_avail  = RelicType.TOPUZ in piece.active_relics

                    if landing_free and can_jump:
                        chains = get_kraljevic_jump_chains(
                            landing_row, landing_col, board, player,
                            row_direction, col_direction, piece,
                            frozenset({(target_row, target_col)}), frozenset()
                        )
                        for (fr, fc, caps, rel) in chains:
                            jump_moves.append((fr, fc, [(target_row, target_col)] + caps, rel))

                        # Topuz kao ALTERNATIVA: direktan udarac bez obaveze lanca
                        if topuz_avail:
                            jump_moves.append((target_row, target_col,
                                               [(target_row, target_col)],
                                               frozenset({RelicType.TOPUZ})))

                    elif topuz_avail:
                        chains = get_kraljevic_jump_chains(
                            target_row, target_col, board, player,
                            row_direction, col_direction, piece,
                            frozenset({(target_row, target_col)}),
                            frozenset({RelicType.TOPUZ})
                        )
                        for (fr, fc, caps, rel) in chains:
                            jump_moves.append((fr, fc, [(target_row, target_col)] + caps, rel))
                    break

                elif piece_on_target.player == player and can_jump:
                    sarac_avail = RelicType.SARAC in piece.active_relics
                    if sarac_avail:
                        landing_row = target_row + row_direction
                        landing_col = target_col + col_direction
                        if (not is_out_of_bounds(landing_row, landing_col) and
                                board.get_piece(landing_row, landing_col) is None):
                            chains = get_kraljevic_jump_chains(
                                landing_row, landing_col, board, player,
                                row_direction, col_direction, piece,
                                frozenset(), frozenset({RelicType.SARAC})
                            )
                            for (fr, fc, caps, rel) in chains:
                                if caps:
                                    jump_moves.append((fr, fc, caps, rel))
                                else:
                                    normal_moves.append((fr, fc, [], rel))
                    break

                else:
                    break

                target_row += row_direction
                target_col += col_direction

    return jump_moves if jump_moves else normal_moves


def get_kraljevic_jump_chains(landing_row, landing_col, board, player,
                               came_from_row_dir, came_from_col_dir, piece,
                               already_captured: frozenset, relics_used: frozenset) -> list:
    """
    Rekurzivna funkcija za lancane skokove Kraljevica.

    piece            -- originalna figura (proveravamo piece.active_relics direktno)
    already_captured -- frozenset koordinata vec pojedenih u ovom lancu
    relics_used      -- frozenset relikvija iskoriscenih u ovom lancu
    """
    topuz_avail = RelicType.TOPUZ in piece.active_relics and RelicType.TOPUZ not in relics_used
    sarac_avail = RelicType.SARAC in piece.active_relics and RelicType.SARAC not in relics_used

    paths = []

    for row_dir in (+1, -1):
        for col_dir in (+1, -1):
            # Ne vracamo se unazad
            if row_dir == -came_from_row_dir and col_dir == -came_from_col_dir:
                continue

            enemy_row     = landing_row + row_dir
            enemy_col     = landing_col + col_dir
            next_land_row = landing_row + 2 * row_dir
            next_land_col = landing_col + 2 * col_dir

            if is_out_of_bounds(enemy_row, enemy_col):
                continue

            piece_at = board.get_piece(enemy_row, enemy_col)
            if piece_at is None:
                continue

            if (piece_at.player != player and piece_at.armor_turns == 0
                    and (enemy_row, enemy_col) not in already_captured):

                next_free = (not is_out_of_bounds(next_land_row, next_land_col) and
                             board.get_piece(next_land_row, next_land_col) is None)

                if next_free:
                    sub = get_kraljevic_jump_chains(
                        next_land_row, next_land_col, board, player,
                        row_dir, col_dir, piece,
                        already_captured | {(enemy_row, enemy_col)}, relics_used
                    )
                    for (fr, fc, caps, rel) in sub:
                        paths.append((fr, fc, [(enemy_row, enemy_col)] + caps, rel))

                elif topuz_avail:
                    sub = get_kraljevic_jump_chains(
                        enemy_row, enemy_col, board, player,
                        row_dir, col_dir, piece,
                        already_captured | {(enemy_row, enemy_col)},
                        relics_used | {RelicType.TOPUZ}
                    )
                    for (fr, fc, caps, rel) in sub:
                        paths.append((fr, fc, [(enemy_row, enemy_col)] + caps, rel))

            elif piece_at.player == player and sarac_avail:
                if (not is_out_of_bounds(next_land_row, next_land_col) and
                        board.get_piece(next_land_row, next_land_col) is None):
                    sub = get_kraljevic_jump_chains(
                        next_land_row, next_land_col, board, player,
                        row_dir, col_dir, piece,
                        already_captured, relics_used | {RelicType.SARAC}
                    )
                    for (fr, fc, caps, rel) in sub:
                        paths.append((fr, fc, caps, rel))

    if not paths:
        return [(landing_row, landing_col, [], relics_used)]
    return paths
