from enum import Enum
from relics import *

class Player(Enum):
    """Dva igraca u igri."""
    BELI = 1   # donja strana table, krece se ka gore
    CRNI = 2   # gornja strana table, krece se ka dole


class PieceType(Enum):
    """Vrste figura."""
    JUNAK = "junak"
    KRALJEVIC = "kraljevic"
    MARKO_KRALJEVIC = "marko"


class Piece:
    """
    Predstavlja jednu figuru na tabli.

    Atributi:
        player        - kom igracu pripada (Player enum)
        piece_type    - vrsta figure (PieceType enum)
        active_relics - lista aktivnih efekata relikvi na ovoj figuri
    """

    def __init__(self, player: Player, piece_type: PieceType = PieceType.JUNAK):
        self.player = player
        self.piece_type = piece_type
        self.active_relics = []
        self.armor_turns = 0
        self.hesitation_turns = 0
        self.mesina_turns = 0       # koliko poteza je Mesina jos "vidljiva" na nasoj figuri
        self.tri_tovara_turns = 0   # > 0 = privremeni Kraljevic; pada na 0 = vracamo na Junaka
        self.unwaivering = False
        self.is_temporary_kraljevic = False
        self.is_permanent_kraljevic = False

    # ------------------------------------------------------------------
    # Status metode
    # ------------------------------------------------------------------

    def is_king(self) -> bool:
        """Vraca True ako je figura kraljevic (ili Marko)."""
        return self.piece_type in (PieceType.KRALJEVIC, PieceType.MARKO_KRALJEVIC)

    def is_marko(self) -> bool:
        return self.piece_type == PieceType.MARKO_KRALJEVIC
    
    def can_promote_to_marko(self) -> bool:
        """Takodje promovise na Marka.
        Uslov: figura ima efekat Kraljevica (trajni ili privremeni) + Sarac + Topuz + Mesina."""
        has_kraljevic_effect = self.is_permanent_kraljevic or RelicType.TRI_TOVARA_BLAGA in self.active_relics
        has_other_relics = {RelicType.SARAC, RelicType.TOPUZ, RelicType.MESINA_RUJNOG_VINA}.issubset(set(self.active_relics))
        if has_kraljevic_effect and has_other_relics and not self.is_marko():
            self.promote_to_marko()
            return True
        return False

    # ------------------------------------------------------------------
    # Promocija
    # ------------------------------------------------------------------

    def promote_to_kraljevic(self):
        """Promovise Junaka u Kraljevica (trajna promocija - dosao na zadnji red)."""
        if self.is_permanent_kraljevic != True:
            self.piece_type = PieceType.KRALJEVIC
            self.is_permanent_kraljevic = True
            self.is_temporary_kraljevic = False
            self.tri_tovara_turns = 0   # trajna promocija, nema reverting
            if RelicType.TRI_TOVARA_BLAGA in self.active_relics:
                self.active_relics.remove(RelicType.TRI_TOVARA_BLAGA)


    def promote_to_kraljevic_temporary(self):
        """Privremena promocija Junaka u Kraljevica (Tri tovara blaga).
        Nema efekta ako je vec stalni Kraljevic ili Marko."""
        if self.piece_type == PieceType.JUNAK or (self.piece_type == PieceType.KRALJEVIC and self.is_temporary_kraljevic == True):
            self.piece_type = PieceType.KRALJEVIC
            self.tri_tovara_turns = 3   # kraj mog poteza + 1 protivnikov + moj sledeci
            self.is_temporary_kraljevic = True

    def promote_to_marko(self):
        """Promovise u Marka Kraljevica (trajna promocija)."""
        self.piece_type = PieceType.MARKO_KRALJEVIC
        self.unwaivering = True
        self.tri_tovara_turns = 0   # trajna promocija, nema reverting
        self.is_permanent_kraljevic = True
        self.is_temporary_kraljevic = False

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
