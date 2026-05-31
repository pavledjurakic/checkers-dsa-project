from game import *
from piece import Player, PieceType
import display as display


def main():
    game = Game()

    while not game.is_game_over(game.board):
        print(f"\nNa potezu je: {game.current_player.name}")
        display.print_board(game.board)
        current_player = game.current_player
        moves = game.get_all_moves(current_player, game.board)

        chosen_figure = input("Izaberite figuru odabirom njene pozicije 'redkolona', npr. '13' >> ")
        row = int(chosen_figure[0])
        col = int(chosen_figure[1])

        available_moves_for_figure = []
        for move in moves:
            if(move.from_row == row and move.from_col == col):
                available_moves_for_figure.append(move)
        
        if not available_moves_for_figure:
            print("Nema dostupih poteza za ovu poziciju - pokusajte ponovo.")
            continue

        display.print_moves(available_moves_for_figure, game.board)
        chosen_move_index = int(input("Unesite broj poteza koji zelite da napravite >> "))
        game.apply_move(available_moves_for_figure[chosen_move_index], game.board)

    print(f"Pobednik je {game.get_winner(game.board)}")


if __name__=="__main__":
    main()
