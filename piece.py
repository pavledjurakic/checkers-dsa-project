from enum import Enum


class Player(Enum):
    """Dva igraca u igri."""
    BELI = 1   # donja strana table, krece se ka vecim redovima (gore vizuelno)
    CRNI = 2   # gornja strana table, krece se ka manjim redovima (dole vizuelno)


class PieceType(Enum):
    """Vrste figura."""
    JUNAK = "junak"                   # obicna figura (pijun)
    KRALJEVIC = "kraljevic"           # promovisana figura (dama)
    MARKO_KRALJEVIC = "marko"         # specijalni kraljevic (sve 4 relikvije)


class Piece:
    """
    Predstavlja jednu figuru na tabli.

    Atributi:
        player        -- kom igracu pripada (Player enum)
        piece_type    -- vrsta figure (PieceType enum)
        active_relics -- lista aktivnih efekata relikvi na ovoj figuri
    """

    def __init__(self, player: Player, piece_type: PieceType = PieceType.JUNAK):
        self.player = player
        self.piece_type = piece_type
        self.active_relics: list = []   # ovde cemo cuvati aktivne efekte (popunjava se kasnije)

    # ------------------------------------------------------------------
    # Status metode
    # ------------------------------------------------------------------

    def is_king(self) -> bool:
        """Vraca True ako je figura kraljevic (ili Marko)."""
        return self.piece_type in (PieceType.KRALJEVIC, PieceType.MARKO_KRALJEVIC)

    def is_marko(self) -> bool:
        return self.piece_type == PieceType.MARKO_KRALJEVIC

    # ------------------------------------------------------------------
    # Promocija
    # ------------------------------------------------------------------

    def promote_to_kraljevic(self):
        """Promovise Junaka u Kraljevica."""
        if self.piece_type == PieceType.JUNAK:
            self.piece_type = PieceType.KRALJEVIC

    def promote_to_marko(self):
        """Promovise Kraljevica u Marka Kraljevica (pasivna sposobnost nepokolebljivosti)."""
        if self.piece_type == PieceType.KRALJEVIC:
            self.piece_type = PieceType.MARKO_KRALJEVIC

    # ------------------------------------------------------------------
    # Pravac kretanja (bitno za Junaka koji ide samo napred)
    # ------------------------------------------------------------------

    def forward_direction(self) -> int:
        """
        Vraca smer napred kao promenu reda:
          BELI krece od reda 7 ka redu 0  ->  -1
          CRNI krece od reda 0 ka redu 7  ->  +1
        """
        return -1 if self.player == Player.BELI else 1

    def promotion_row(self) -> int:
        """Red na kome Junak dobija promociju."""
        return 0 if self.player == Player.BELI else 7

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"Piece({self.player.name}, {self.piece_type.name})"
