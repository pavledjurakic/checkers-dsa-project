# Za konzolni prikaz
from piece import *
from relics import RelicType

# Background and druge boje - ANSI kodovi:
WHITE = '[37;1m'  # beli igrac
RED = '[31;1m'    # tamno braon  — crni igrac
BG_LITE = '[47m'  # svetla pozadina — belo polje
BG_CYAN = '[46m'  # highlighted potez
BG_PINK = '[45m'  # brazda
END = '\033[0m'


def _sym(piece):
    return "J" if piece.piece_type == PieceType.JUNAK else ("K" if piece.piece_type == PieceType.KRALJEVIC else "M")


def _relic_str(piece):
    """relic indikator, npr. 'T·P··'. Prazno ako nema relikvija.
    T=Toka, M=Mesina, P=toPuz, S=Sarac, B=tri tovara Blaga"""
    if not piece.active_relics:
        return '     '
    order   = [RelicType.TOKA_OD_CELIKA, RelicType.MESINA_RUJNOG_VINA,
               RelicType.TOPUZ, RelicType.SARAC, RelicType.TRI_TOVARA_BLAGA]
    letters = ['T', 'M', 'P', 'S', 'B']
    return ''.join(l if r in piece.active_relics else '·' for r, l in zip(order, letters))


def print_board(board, highlighted=[]):
    SEP = "   " + "+-----" * 8 + "+"

    print("      0     1     2     3     4     5     6     7")
    print(SEP)

    for row in range(8):
        piece_line = f" {row} "
        relic_line = "   "

        for col in range(8):
            sq = board.get_square(row, col)

            if (row, col) in highlighted:
                piece_line += f"|{BG_CYAN}  *  {END}"
                relic_line += f"|{BG_CYAN}     {END}"
            elif not sq.is_usable:
                piece_line += f"|{BG_LITE}     {END}"
                relic_line += f"|{BG_LITE}     {END}"
            elif sq.is_brazda:
                if not sq.piece:
                    piece_line += f"|{BG_PINK}  ~  {END}"
                    relic_line += f"|{BG_PINK}     {END}"
                else:
                    color = WHITE if sq.piece.player == Player.BELI else RED
                    piece_line += f"|{BG_PINK}{color}  {_sym(sq.piece)}  {END}"
                    relic_line += f"|{BG_PINK}{color}{_relic_str(sq.piece)}{END}"
            else:
                if not sq.piece:
                    piece_line += f"|  ·  "
                    relic_line += f"|     "
                else:
                    color = WHITE if sq.piece.player == Player.BELI else RED
                    piece_line += f"|{color}  {_sym(sq.piece)}  {END}"
                    relic_line += f"|{color}{_relic_str(sq.piece)}{END}"

        print(piece_line + "|")
        print(relic_line + "|")
        print(SEP)


def print_moves(moves, board):
    highlighted = [(m.to_row, m.to_col) for m in moves]
    print_board(board, highlighted)

    print("\nDostupni potezi:")
    for i, m in enumerate(moves):
        if m.captured:
            print(f"  {i}: ({m.from_row},{m.from_col}) -> ({m.to_row},{m.to_col})  [jede: {m.captured}]")
        else:
            print(f"  {i}: ({m.from_row},{m.from_col}) -> ({m.to_row},{m.to_col})")
