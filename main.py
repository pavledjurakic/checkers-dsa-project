from game import *
from piece import Player, PieceType
from relics import *
import display as display


def main():
    game = Game()

    while not game.is_game_over(game.board):
        print(f"\nNa potezu je: {game.current_player.name}")
        display.print_board(game.board)
        current_player = game.current_player
        moves = game.get_all_moves(current_player, game.board)
        
        figure_sa_potezima = sorted(set((m.from_row, m.from_col) for m in moves))
        print(f"Figure koje mogu da se igraju: {figure_sa_potezima}")

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
        chosen_move = available_moves_for_figure[chosen_move_index]
        game.apply_move(chosen_move, game.board)
        
        target_square = game.board.get_square(chosen_move.to_row, chosen_move.to_col)
        if target_square.is_brazda:
            print("Dobrodosli na Carev Drum - izaberite relikviju (1/2):")
            print(f"1. {game.tsar_road.peek_front()}")
            print(f"2. {game.tsar_road.peek_rear()}")
            choice = int(input(">> "))
            match choice:
                case 1:
                    relic = game.tsar_road.get_front()
                    target_square.piece.active_relics.append(relic)
                    if relic == RelicType.TRI_TOVARA_BLAGA:
                        target_square.piece.promote_to_kraljevic()
                    elif relic == RelicType.TOKA_OD_CELIKA:
                        target_square.piece.armor_turns = 2 if target_square.piece.is_marko() else 1
                    elif relic == RelicType.MESINA_RUJNOG_VINA:
                        nearest_enemy_squares = game.board.get_nearest_enemy(target_square.row,target_square.col)
                        # To Do - jos samo da se ovde kasnije ubaci da se zapravo bira ona koja je najjaca figura, a da nije otporna da se mami u heuristici
                        if nearest_enemy_squares[0].piece.unwaivering==False: nearest_enemy_squares[0].piece.hesitation_turns = 2

                case 2:
                    relic = game.tsar_road.get_rear()
                    target_square.piece.active_relics.append(relic)
                    if relic == RelicType.TRI_TOVARA_BLAGA:
                        target_square.piece.promote_to_kraljevic()
                    elif relic == RelicType.TOKA_OD_CELIKA:
                        target_square.piece.armor_turns = 2 if target_square.piece.is_marko() else 1
                    elif relic == RelicType.MESINA_RUJNOG_VINA:
                        nearest_enemy_squares = game.board.get_nearest_enemy(target_square.row,target_square.col)
                        # To Do - jos samo da se ovde kasnije ubaci da se zapravo bira ona koja je najjaca figura, a da nije otporna da se mami u heuristici
                        if nearest_enemy_squares[0].piece.unwaivering==False: nearest_enemy_squares[0].piece.hesitation_turns = 2

            
            if target_square.piece.can_promote_to_marko():
                print("Vasa figura je postala Marko Kraljevic - sada ima pasivnu sposobnost nepokolebljivosti.")

        game.board.decrement_relics_count()

    print(f"Pobednik je {game.get_winner(game.board)}")


if __name__=="__main__":
    main()
