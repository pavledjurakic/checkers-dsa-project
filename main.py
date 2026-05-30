from board import Board
from piece import Player, PieceType


def main():
    board = Board()

    # --- Osnovna provera ---
    beli = board.get_all_pieces(Player.BELI)
    crni = board.get_all_pieces(Player.CRNI)
    print(f"Tabla kreirana: {Board.ROWS}x{Board.COLS}")
    print(f"Beli figure:  {len(beli)}  (ocekivano 12)")
    print(f"Crni figure:  {len(crni)}  (ocekivano 12)")

    # --- Provera brazdi ---
    brazde = [sq for sq in board.grid if sq.is_brazda]
    
    print(f"\nBrazde na lokacijama: {[sq.location for sq in brazde]}")
    print(f"  (ocekivano: [(3, 0), (4, 7)])")

    # --- Provera neaktivnih polja (bela polja) ---
    neaktivna = sum(
        1 for sq in board.grid if not sq.is_usable
    )
    print(f"\nNeaktivnih (belih) polja: {neaktivna}  (ocekivano 32)")

    print("\nSve OK!")


if __name__ == "__main__":
    main()
