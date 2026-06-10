from ai.heuristics import *
from math import inf
from game import Game
import copy, time
import ai.zobrist_hashing as z_hash
from ai.timeout_exception import TimeoutException


def clone_game(game):
    g = copy.deepcopy(game)
    g.undo_stack = []
    return g


def apply_game(game, move):
    from_sq = game.board.get_square(move.from_row, move.from_col)
    to_sq = game.board.get_square(move.to_row,   move.to_col)

    for (row, col) in move.captured:
        game.board.get_square(row, col).piece = None

    game.board.move_piece(from_sq, to_sq)
    game.board.check_promotion(to_sq)

    if RelicType.TOPUZ in move.relics_used and to_sq.piece:
        to_sq.piece.active_relics.remove(RelicType.TOPUZ)

    if to_sq.is_brazda and to_sq.piece and game.tsar_road:
        pick_best_relic(game, to_sq)
        to_sq.piece.can_promote_to_marko()

    game.board.decrement_relics_count()
    game.tsar_road.backfill()


def pick_best_relic(game, to_sq):
    """AI automatski bira bolju od dve relikvije na brazdi."""
    front = game.tsar_road.peek_front()
    rear  = game.tsar_road.peek_rear()

    score_front = score_relic(front, to_sq.piece, game)
    score_rear = score_relic(rear,  to_sq.piece, game)

    if score_front >= score_rear:
        relic = game.tsar_road.get_front()
    else:
        relic = game.tsar_road.get_rear()

    apply_relic(game, to_sq, relic)
    return relic


def score_relic(relic, piece, game):
    """Gruba procena vrednosti relikvije za datu figuru."""
    if relic == RelicType.TOKA_OD_CELIKA:
        turns = 4 if piece.is_marko() else 2
        return turns * 50
    if relic == RelicType.TOPUZ:
        return 80
    if relic == RelicType.MESINA_RUJNOG_VINA:
        return 60
    if relic == RelicType.SARAC:
        return 30
    if relic == RelicType.TRI_TOVARA_BLAGA and not piece.is_permanent_kraljevic: # ne zelimo za trajnog kraljevica da pumpamo skor, kada njemu ovo ne znaci nista
        return 50
    return 0


def apply_relic(game, to_sq, relic):
    piece = to_sq.piece
    if relic == RelicType.TRI_TOVARA_BLAGA and piece.is_permanent_kraljevic != True:
        if relic not in piece.active_relics:
            piece.active_relics.append(relic)
        piece.promote_to_kraljevic_temporary()
    elif relic == RelicType.TOKA_OD_CELIKA:
        if relic not in piece.active_relics:
            piece.active_relics.append(relic)
        piece.armor_turns = 4 if piece.is_marko() else 2
    elif relic == RelicType.MESINA_RUJNOG_VINA:
        if relic not in piece.active_relics:
            piece.active_relics.append(relic)
        nearest = game.board.get_nearest_enemy(to_sq.row, to_sq.col)
        if nearest and not nearest[0].piece.unwaivering:
            nearest[0].piece.hesitation_turns = 4
        piece.mesina_turns = 4
    elif relic == RelicType.SARAC or relic == RelicType.TOPUZ:
        piece.active_relics.append(relic)


def minimax(game, depth, alpha, beta, is_maximizing, transposition_table, start_time, time_limit):
    if time.time() - start_time >= time_limit:
        raise TimeoutException()
    player = Player.BELI if is_maximizing else Player.CRNI
    moves  = Game.get_all_moves(None, player, game.board)

    if depth == 0 or not moves:
        return evaluate_game_state(game.board)

    if is_maximizing:  # BELI
        best = -inf
        for move in moves:
            game_copy = clone_game(game)
            apply_game(game_copy, move)

            pos_hash = z_hash.compute_hash(game_copy.board, Player.CRNI)

            if pos_hash in transposition_table and transposition_table[pos_hash][1] >= depth:
                score = transposition_table[pos_hash][0]
            else:
                score = minimax(game_copy, depth-1, alpha, beta, False, transposition_table, start_time, time_limit)
                transposition_table[pos_hash] = [score, depth]

            best  = max(best, score)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best

    else:  # CRNI
        best = +inf
        for move in moves:
            game_copy = clone_game(game)
            apply_game(game_copy, move)

            pos_hash = z_hash.compute_hash(game_copy.board, Player.BELI)

            if pos_hash in transposition_table and transposition_table[pos_hash][1] >= depth:
                score = transposition_table[pos_hash][0]
            else:
                score = minimax(game_copy, depth-1, alpha, beta, True, transposition_table, start_time, time_limit)
                transposition_table[pos_hash] = [score, depth]
            
            best = min(best, score)
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best


def get_best_move(game, is_maximizing, depth, transposition_table, start_time, time_limit):
    best_move = None
    best_score = -inf if is_maximizing else +inf
    player = Player.BELI if is_maximizing else Player.CRNI

    for move in Game.get_all_moves(None, player, game.board):
        game_copy = clone_game(game)
        apply_game(game_copy, move)

        pos_hash = z_hash.compute_hash(game_copy.board, Player.CRNI if is_maximizing else Player.BELI)

        if pos_hash in transposition_table and transposition_table[pos_hash][1] >= depth:
            score = transposition_table[pos_hash][0]
        else:
            try:
                score = minimax(game_copy, depth-1, -inf, +inf, not is_maximizing, transposition_table, start_time, time_limit)
            except TimeoutException:
                return None
            transposition_table[pos_hash] = [score, depth]

        if is_maximizing and score > best_score:
            best_score = score
            best_move  = move
        elif not is_maximizing and score < best_score:
            best_score = score
            best_move  = move
        
    return best_move


def get_best_move_iteratively(game, is_maximizing, time_limit=3.0):
    transposition_table = {}
    best_move = None
    last_duration = 0
    start = time.time()

    for depth in range(1, 20):
        if time.time() - start + last_duration > time_limit:
            break
        t = time.time()
        move = get_best_move(game, is_maximizing, depth, transposition_table, start, time_limit)
        last_duration = time.time() - t
        if move is not None:
            best_move = move  # cuvamo samo kompletne rezultate

    return best_move
