from square import Square
from piece import Piece, Player, PieceType


class Board:
    """
    Predstavlja tablu 8x8.

    Interna struktura:
        self.grid  --  niz Square objekata, indeksirana sa grid[row][col]
    """

    ROWS = 8
    COLS = 8

    def __init__(self):
        # Pravi 8x8 mrezu Square objekata ka 1D niz
        self.grid = []

        for row in range (0,8,1):
            for col in range (0,8,1):
                self.grid.append(Square(row, col))

        self._setup_pieces()

    # ------------------------------------------------------------------
    # Inicijalno postavljanje figura
    # ------------------------------------------------------------------

    def _setup_pieces(self):
        """
        Postavlja pocetno stanje:
          CRNI -- gornja strana, redovi 0-2 (tamna polja)
          BELI -- donja strana, redovi 5-7 (tamna polja)
          Redovi 3 i 4 su prazni.
        """

        for row in range(0,3,1):
            for col in range(0,8,1):
                sq = self.grid[row*8 +col]
                if sq.is_usable:
                    sq.piece = Piece(Player.CRNI)

        for row in range(5,8,1):
            for col in range(0,8,1):
                sq = self.grid[row*8 + col]
                if sq.is_usable:
                    sq.piece = Piece(Player.BELI)

    # ------------------------------------------------------------------
    # Pristup poljima i figurama
    # ------------------------------------------------------------------

    def get_square(self, row: int, col: int) -> Square | None:
        """Vraca Square na (row, col). None ako je van granica."""
        if 0 <= row < self.ROWS and 0 <= col < self.COLS:
            return self.grid[row*8 +col]
        return None

    def get_piece(self, row: int, col: int) -> Piece | None:
        """Vraca figuru na (row, col). None ako je van granica ili prazno."""
        sq = self.get_square(row, col)
        return sq.piece if sq else None

    def get_all_pieces(self, player: Player) -> list[tuple[Piece, Square]]:
        """Vraca sve figure zadatog igraca kao listu (figura, polje)."""
        result = []
        for square in self.grid:
            if square.piece and square.piece.player == player:
                result.append((square.piece, square))
        return result

    # ------------------------------------------------------------------
    # Pomeranje i uklanjanje figura
    # ------------------------------------------------------------------

    def move_piece(self, from_sq: Square, to_sq: Square):
        """
        Premesta figuru sa from_sq na to_sq.
        Ne proverava ispravnost poteza - to radi game logika.
        """
        to_sq.piece = from_sq.piece
        from_sq.piece = None

    def remove_piece(self, sq: Square):
        """Uklanja figuru sa polja (jedenje protivnicke figure)."""
        sq.piece = None


    # ------------------------------------------------------------------
    # Provera promocije i maintanence relikvija
    # ------------------------------------------------------------------

    def check_promotion(self, sq: Square):
        """
        Ako figura na datom polju treba da bude promovisana, promovise je.
        Poziva se nakon svakog poteza.
        """
        piece = sq.piece
        if piece is None:
            return
        if piece.piece_type == PieceType.JUNAK and sq.row == piece.promotion_row():
            piece.promote_to_kraljevic()

    def decrement_relics_count(self):
        """
        Prolazi kroz sve figure na tabli i za relic effect count >0 smanjuje im za 1.
        Biva pozivano na kraju svakog poteza.
        """
        for square in self.grid:
            if square.is_usable and square.piece:
                if square.piece.armor_turns > 0: square.armor_turns-=1
                if square.piece.hesitation_turns > 0 : square.hesitation_turns-=1
        

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"Board(beli={len(self.get_all_pieces(Player.BELI))}, crni={len(self.get_all_pieces(Player.CRNI))})"
