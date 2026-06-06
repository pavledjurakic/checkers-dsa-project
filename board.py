from square import Square
from piece import Piece, Player, PieceType
from relics import RelicType

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


    def get_nearest_enemy(self, row: int, col: int) -> list[Square] | None:   # trazi po nivoima udaljenost kruzno i vraca sve koje su najlizi na istoj udaljenosti
        for distance in range(1,8):
            found = []

            directions = [(-distance,-distance),(-distance,distance),(distance,-distance),(distance,distance)]
            for dx, dy in directions:
                x = row + dx
                y = col + dy

                if 0 <= x < self.ROWS and 0 <= y < self.COLS:
                    if self.get_piece(x,y) is not None and self.get_piece(x,y).player != self.get_piece(row,col).player:
                        found.append(self.get_square(x,y))
            
            if found:
                return found
        return None


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
            if not square.is_usable or not square.piece:
                continue
            piece = square.piece

            if piece.armor_turns > 0:
                piece.armor_turns -= 1
                if piece.armor_turns == 0 and RelicType.TOKA_OD_CELIKA in piece.active_relics:
                    piece.active_relics.remove(RelicType.TOKA_OD_CELIKA)

            if piece.hesitation_turns > 0:
                piece.hesitation_turns -= 1

            if piece.mesina_turns > 0:
                piece.mesina_turns -= 1
                if piece.mesina_turns == 0 and RelicType.MESINA_RUJNOG_VINA in piece.active_relics:
                    piece.active_relics.remove(RelicType.MESINA_RUJNOG_VINA)

            if piece.tri_tovara_turns > 0:
                piece.tri_tovara_turns -= 1
                if piece.tri_tovara_turns == 0 and piece.piece_type == PieceType.KRALJEVIC:
                    piece.piece_type = PieceType.JUNAK
                    if RelicType.TRI_TOVARA_BLAGA in piece.active_relics:
                        piece.active_relics.remove(RelicType.TRI_TOVARA_BLAGA)
        

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"Board(beli={len(self.get_all_pieces(Player.BELI))}, crni={len(self.get_all_pieces(Player.CRNI))})"
