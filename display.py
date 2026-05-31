# Za konzolni prikaz
from piece import *

# Background and other colors - ANSI codes:
WHITE = '\u001b[37;1m'      # beli igrac
RED = '\u001b[31;1m'    # tamno braon  — crni igrac
BG_LITE = '[47m'      # svetla pozadina — belo polje
BG_CYAN = '[46m'      # highlighted potez
BG_PINK = '[45m'      # brazda
END         = '\033[0m'


def print_board(board, highlighted=[]):
    for row in range(8):
        if row == 0:
            print("    0  1  2  3  4  5  6  7")
            print("  __________________________")
        for col in range(8):
            if col == 0:
                print(row, end=" |")
            sq = board.get_square(row, col)

            if (row, col) in highlighted:
                print(f"{BG_CYAN} * {END}", end="")
            elif not sq.is_usable:
                print(f"{BG_LITE}   {END}", end="")
            elif sq.is_brazda:
                if not sq.piece:
                    print(f"{BG_PINK} ~ {END}", end="")
                else:
                    color = WHITE if sq.piece.player == Player.BELI else RED
                    sym = "J" if sq.piece.piece_type == PieceType.JUNAK else ("K" if sq.piece.piece_type == PieceType.KRALJEVIC else "M")
                    print(f"{BG_PINK}{color} {sym} {END}", end="")
            else:
                if not sq.piece:
                    print(f" · ", end="")
                else:
                    color = WHITE if sq.piece.player == Player.BELI else RED
                    sym = "J" if sq.piece.piece_type == PieceType.JUNAK else ("K" if sq.piece.piece_type == PieceType.KRALJEVIC else "M")
                    print(f"{color} {sym} {END}", end="")
        print("|")


def print_moves(moves, board):
    highlighted = [(m.to_row, m.to_col) for m in moves]
    print_board(board, highlighted)

    print("\nDostupni potezi:")
    for i, m in enumerate(moves):
        if m.captured:
            print(f"  {i}: ({m.from_row},{m.from_col}) -> ({m.to_row},{m.to_col})  [jede: {m.captured}]")
        else:
            print(f"  {i}: ({m.from_row},{m.from_col}) -> ({m.to_row},{m.to_col})")

