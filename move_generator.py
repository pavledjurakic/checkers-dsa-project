from board import Board
from piece import Player, PieceType
from square import Square


def get_moves(square: Square, board: Board) -> list:
    """
    Glavna funkcija. Prima polje i tablu.
    Vraca listu validnih poteza za figuru na tom polju.

    Svaki potez je tuple oblika:
        (to_row, to_col, [lista (row,col) pojedenih neprijatelja])

    Primeri:
        (3, 4, [])                    <- normalan potez, niko nije pojeden
        (1, 6, [(4, 3)])              <- skok, pojeden neprijatelj na (4,3)
        (1, 2, [(4, 3), (2, 1)])      <- lancani skok, pojeeni dvoje
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
    """
    Generise poteze za Junaka.

    Junak se krece samo NAPRED dijagonalno za 1 polje.
    Ako postoji ijedan skok - normalni potezi su zabranjeni (jedenje je obavezno).
    """
    player    = square.piece.player
    row_dir   = square.piece.forward_direction()   # BELI: -1, CRNI: +1

    normal_moves = []
    jump_moves   = []

    for col_dir in (+1, -1):   # leva i desna dijagonala
        target_row = square.row + row_dir
        target_col = square.col + col_dir

        if is_out_of_bounds(target_row, target_col):
            continue

        piece_on_target = board.get_piece(target_row, target_col)

        if piece_on_target is None:
            # Prazno polje - normalan potez
            normal_moves.append((target_row, target_col, []))

        elif piece_on_target.player != player:
            # Neprijatelj - proveri da li je landing slobodan
            landing_row = square.row + 2 * row_dir
            landing_col = square.col + 2 * col_dir

            if is_out_of_bounds(landing_row, landing_col):
                continue
            if board.get_piece(landing_row, landing_col) is not None:
                continue    # landing je zauzet, skok nije moguc

            # Skok je moguc — pronadji sve lance od landing pozicije
            already_captured = {(target_row, target_col)}
            chains = get_junak_jump_chains(landing_row, landing_col, board, player, row_dir, already_captured)

            for (final_row, final_col, more_caps) in chains:
                jump_moves.append( (final_row, final_col, [(target_row, target_col)] + more_caps) )

    # Jedenje je obavezno — ako ima skokova, normalni potezi se ignorisu 
    return jump_moves if jump_moves else normal_moves


def get_junak_jump_chains(landing_row: int, landing_col: int, board: Board, player: Player, row_dir: int, already_captured: set) -> list:
    """
    Rekurzivna funkcija. Poziva se sa landing pozicije nakon skoka.
    Trazi sve moguce dalje lance skokova od te pozicije.

    Vraca listu (final_row, final_col, [dalje_pojedeni]) za svaki moguci put.
    Ako nema daljeg skakanja, vraca [(landing_row, landing_col, [])].

    already_captured: skup vec pojedenih figura u ovom lancu (ne smemo preskociti isti komad dva puta)
    """
    paths = []

    for col_dir in (+1, -1):
        enemy_row = landing_row + row_dir
        enemy_col = landing_col + col_dir
        next_landing_row = landing_row + 2 * row_dir
        next_landing_col = landing_col + 2 * col_dir

        if is_out_of_bounds(enemy_row, enemy_col):
            continue
        if is_out_of_bounds(next_landing_row, next_landing_col):
            continue

        enemy = board.get_piece(enemy_row, enemy_col)
        next_landing = board.get_piece(next_landing_row, next_landing_col)

        enemy_is_capturable = (
            enemy is not None
            and enemy.player != player
            and enemy.armor_turns == 0
            and next_landing is None
            and (enemy_row, enemy_col) not in already_captured
        )

        if enemy_is_capturable:
            new_captured = already_captured | {(enemy_row, enemy_col)}
            sub_paths = get_junak_jump_chains(next_landing_row, next_landing_col, board, player, row_dir, new_captured)
            for (final_row, final_col, more_caps) in sub_paths:
                paths.append( (final_row, final_col, [(enemy_row, enemy_col)] + more_caps) )

    # Nema vise skokova - ova landing pozicija je konacna
    if not paths:
        return [(landing_row, landing_col, [])]

    return paths


# ============================================
# KRALJEVIC  (i MARKO KRALJEVIC - isti pokret)
# ============================================

def get_kraljevic_moves(square: Square, board: Board) -> list:
    """
    Kraljevic se krece dijagonalno u sva 4 smera, koliko god polja.
    """

    player = square.piece.player
    normal_moves = []
    jump_moves = []


    for col_direction in (+1,-1):
        for row_direction in (+1,-1):
            target_row = square.row + row_direction
            target_col = square.col + col_direction
            
            while not is_out_of_bounds(target_row, target_col):
                piece_on_target = board.get_piece(target_row, target_col)
                
                if piece_on_target is None:
                    normal_moves.append((target_row, target_col, []))

                elif piece_on_target.player != player:
                    landing_row = target_row + row_direction
                    landing_col = target_col + col_direction

                    if is_out_of_bounds(landing_row, landing_col):
                        break
                    if board.get_piece(landing_row, landing_col) is not None:
                        break

                    already_captured = {(target_row, target_col)}

                    chains = get_kraljevic_jump_chains(landing_row, landing_col, board, player, row_direction, col_direction, already_captured)

                    for (final_row, final_col, more_caps) in chains:
                        jump_moves.append( (final_row, final_col, [(target_row, target_col)] + more_caps) )
                    
                    break
                
                target_row += row_direction
                target_col += col_direction

    # Jedenje je obavezno — ako ima skokova, normalni potezi se ignorisu 
    return jump_moves if jump_moves else normal_moves


def get_kraljevic_jump_chains(landing_row, landing_col, board, player, came_from_row_dir, came_from_col_dir, already_captured):
    """
    Rekurzivna funkcija. Poziva se sa landing pozicije nakon skoka kraljevica.
    Trazi sve moguce dalje lance skokova od te pozicije u svim pravcima osim odakle je dosao, da ne pojede 2 puta istog.

    Vraca listu (final_row, final_col, [dalje_pojedeni]) za svaki moguci put.
    Ako nema daljeg skakanja, vraca [(landing_row, landing_col, [])].

    already_captured: skup vec pojedenih figura u ovom lancu (ne smemo preskociti isti komad dva puta)
    """
    paths = []
    
    for row_dir in (+1, -1):
        for col_dir in (+1, -1):
            if row_dir == -came_from_row_dir and col_dir == -came_from_col_dir:
                continue
            
            enemy_row = landing_row + row_dir
            enemy_col = landing_col + col_dir
            next_landing_row = landing_row + 2 * row_dir
            next_landing_col = landing_col + 2 * col_dir

            if is_out_of_bounds(enemy_row, enemy_col):
                continue
            if is_out_of_bounds(next_landing_row, next_landing_col):
                continue

            enemy = board.get_piece(enemy_row, enemy_col)
            next_landing = board.get_piece(next_landing_row, next_landing_col)

            enemy_is_capturable = (
                enemy is not None
                and enemy.player != player
                and enemy.armor_turns == 0
                and next_landing is None
                and (enemy_row, enemy_col) not in already_captured
            )

            if enemy_is_capturable:
                new_captured = already_captured | {(enemy_row, enemy_col)}
                sub_paths = get_kraljevic_jump_chains(next_landing_row, next_landing_col, board, player, row_dir, col_dir, new_captured)
                for (final_row, final_col, more_caps) in sub_paths:
                    paths.append( (final_row, final_col, [(enemy_row, enemy_col)] + more_caps) )

    # Nema vise skokova - ova landing pozicija je konacna
    if not paths:
        return [(landing_row, landing_col, [])]

    return paths
