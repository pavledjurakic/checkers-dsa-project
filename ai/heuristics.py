from board import *
from piece import *
from game import Game


def evaluate_game_state(board: Board) -> int:
    score = 0
    CENTER_BONUS = [0, 0, 2, 3, 3, 2, 0, 0]

    squares = []

    for row in range(0,8,1):
        for col in range(0,8,1):
            sq = board.get_square(row, col)
            if sq.is_usable:
                squares.append(sq)


    for square in squares:
         if square.piece:
            if square.piece.player == Player.CRNI:
                multiply = -1
                advancement = square.row
            else: 
                multiply = +1
                advancement = 7 - square.row
            
            # Bazicna evaulacija na osnovu tipova i broja figura
            if square.piece.piece_type == PieceType.JUNAK:
                score += multiply * 100
                score += multiply * (advancement * 4)
                score += multiply * CENTER_BONUS[square.col]
            elif square.piece.piece_type == PieceType.KRALJEVIC:
                score += multiply * 300
                # mogao bih da ubacim porveru za advancement temporary kraljevica
                score += multiply * CENTER_BONUS[square.col]
            elif square.piece.piece_type == PieceType.MARKO_KRALJEVIC:
                score += multiply * 500
                score += multiply * CENTER_BONUS[square.col]

            # Figura na zadnjem redu sprečava protivničku promociju
            if square.piece.player == Player.CRNI and square.row == 0:
                score += multiply * 8
            if square.piece.player == Player.BELI and square.row == 7:
                score += multiply * 8

            # Relikvije
            if RelicType.TOKA_OD_CELIKA in square.piece.active_relics:
                score += multiply * (square.piece.armor_turns * 50)   # proporcijalno preostatku
            if RelicType.TOPUZ in square.piece.active_relics:
                score += multiply * 80
            if (square.piece.mesina_turns > 0):
                score += multiply * 60
            if RelicType.SARAC in square.piece.active_relics:
                score += multiply * 30
            if RelicType.TRI_TOVARA_BLAGA in square.piece.active_relics:
                score += multiply * 50

            # Hesitation penali
            if square.piece.hesitation_turns > 0:
                score -= multiply * (square.piece.hesitation_turns * 20)

    # Mobilnost (opcionalno, jer je skupo)
    """Broj poteza koji AI ima vs protivnik
       Uglavnom se izostavlja na leaf nodovima, ali moze da se doda uz flag samo za depth==0
    """
    beli_turns = len(Game.get_all_moves(None, Player.BELI, board))
    crni_turns = len(Game.get_all_moves(None, Player.CRNI, board))
    score += (beli_turns - crni_turns) * 5

    return score

