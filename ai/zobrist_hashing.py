from board import *


def compute_hash(board: Board) -> int:
    hash = 0

    for row in range (0,8,1):
        for col in range (0,8,1):
            square = board.get_square(row, col)
            if square.is_usable and square.piece:
                if square.piece.player == Player.BELI:
                    hash = hash ^ square.hashes["BELI"]
                else:
                    hash = hash ^ square.hashes["CRNI"]

                if square.piece.piece_type == PieceType.JUNAK:
                    hash = hash ^ square.hashes["JUNAK"]
                elif square.piece.piece_type == PieceType.KRALJEVIC:
                    hash = hash ^ square.hashes["KRALJEVIC"]
                elif square.piece.piece_type == PieceType.MARKO_KRALJEVIC:
                    hash = hash ^ square.hashes["MARKO_KRALJEVIC"]
                
                for relic in square.piece.active_relics:
                    hash = hash ^ square.hashes[relic.name]
    
    return hash
