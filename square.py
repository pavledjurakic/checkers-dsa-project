class Square:
    """
    Predstavlja jedno polje na tabli.

    Atributi:
        row, col    -- pozicija u mreži (0-7)
        location    -- (row, col) tuple, za brzi pristup
        is_usable   -- True samo za tamna polja (jedina aktivna u Dami)
        piece       -- objekat figure koja stoji na polju, ili None
        is_brazda   -- True za specijalna polja (3,0) i (4,7)
    """

    BRAZDE_LOKACIJE = {(3, 0), (4, 7)}

    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.location = (row, col)
        self.is_usable = (row + col) % 2 == 1   # tamna polja imaju zbir nep. broj
        self.piece = None
        self.is_brazda = self.location in self.BRAZDE_LOKACIJE

    # ------------------------------------------------------------------
    # Pomocne metode
    # ------------------------------------------------------------------

    def is_empty(self) -> bool:
        """Vraca True ako nema figure na polju."""
        return self.piece is None

    def has_piece(self) -> bool:
        return self.piece is not None

    def __repr__(self) -> str:
        extras = []
        if not self.is_usable:
            extras.append("neaktivno")
        if self.is_brazda:
            extras.append("BRAZDA")
        if self.piece:
            extras.append(str(self.piece))
        info = ", ".join(extras) if extras else "prazno"
        return f"Square({self.row},{self.col}) [{info}]"
