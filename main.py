from game import *
from piece import Player, PieceType
from relics import *
import display as display
import ai.minimax as ai_minmax
import time
from data_structures.n_ary_tree import *

def main():
    game = Game()
    n_ary_tree = N_Ary_Tree(game.board)
    while True:
        choice = input("Da li zelite da budete CRNI(1) ili BELI(2) igrac >> ")
        if choice in ["1", "2"]:
            int_choice = int(choice)
            match int_choice:
                case 1:
                    game.human_player = Player.CRNI
                    game.ai_player = Player.BELI
                    break
                case 2:
                    game.human_player = Player.BELI
                    game.ai_player = Player.CRNI
                    break
        print("Niste uneli validnu opciju 1/2 - pokusajte ponovo!")
    

    while not game.is_game_over(game.board):
        time.sleep(1)
        print("="*15)
        print(f"\nNa potezu je: {game.current_player.name}")
        display.print_board(game.board)
        current_player = game.current_player
        moves = game.get_all_moves(current_player, game.board)

        if not moves: # igrac nema vise nista da odigra, protivnik je pobedio
            game.winner = Player.CRNI if current_player != Player.CRNI else Player.BELI
            n_ary_tree.current_node.is_game_over = True
            break
        
        figure_sa_potezima = sorted(set((m.from_row, m.from_col) for m in moves))
        print(f"Figure koje mogu da se igraju: {figure_sa_potezima}")

        if current_player == game.ai_player:

            best_move = ai_minmax.get_best_move_iteratively(game, True if game.ai_player==Player.BELI else False, 3)
            print(f"AI: ({best_move.from_row},{best_move.from_col}) -> ({best_move.to_row},{best_move.to_col})", end="")
            if best_move.captured:
                print(f"  [jede: {best_move.captured}]", end="")
            print()
            game.apply_move(best_move, game.board)
            n_ary_tree.add_next_move(best_move, game.board) # za reprodukciju kasnije

            target_square = game.board.get_square(best_move.to_row, best_move.to_col)
            if target_square.is_brazda:

                choice = ai_minmax.pick_best_relic(game, target_square)
                print(f"AI je odabrao relikviju: {choice}.")

                if target_square.piece.can_promote_to_marko():
                    print("AI figura je postala Marko Kraljevic - sada ima pasivnu sposobnost nepokolebljivosti.")


        else:

            chosen_figure = input("Izaberite figuru odabirom njene pozicije 'redkolona', npr. '13' ili unesite 'undo' za undo >> ")
            if chosen_figure == 'undo':
                game.undo()
                n_ary_tree.current_node = n_ary_tree.current_node.parent
                continue
            else:
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
            if chosen_move_index < 0 or chosen_move_index >= len(available_moves_for_figure):
                print(f"Neispravan broj poteza. Unesite broj od 0 do {len(available_moves_for_figure)-1}.")
                continue
            chosen_move = available_moves_for_figure[chosen_move_index]
            game.apply_move(chosen_move, game.board)
            n_ary_tree.add_next_move(chosen_move, game.board) # za reprodukciju kasnije
            
            target_square = game.board.get_square(chosen_move.to_row, chosen_move.to_col)
            if target_square.is_brazda:
                print("Dobrodosli na Carev Drum - izaberite relikviju (1/2):")
                print(f"1. {game.tsar_road.peek_front()}")
                print(f"2. {game.tsar_road.peek_rear()}")
                choice = int(input(">> "))
                match choice:
                    case 1:
                        relic = game.tsar_road.get_front()
                        if relic == RelicType.TRI_TOVARA_BLAGA and target_square.piece.is_permanent_kraljevic != True:
                            target_square.piece.active_relics.append(relic)
                            target_square.piece.promote_to_kraljevic_temporary()
                        elif relic == RelicType.TOKA_OD_CELIKA:
                            target_square.piece.active_relics.append(relic)
                            target_square.piece.armor_turns = 4 if target_square.piece.is_marko() else 2
                        elif relic == RelicType.MESINA_RUJNOG_VINA:
                            target_square.piece.active_relics.append(relic)
                            nearest_enemy_squares = game.board.get_nearest_enemy(target_square.row,target_square.col)
                            # To Do - jos samo da se ovde kasnije ubaci da se zapravo bira ona koja je najjaca figura, a da nije otporna da se mami u heuristici
                            if nearest_enemy_squares and nearest_enemy_squares[0].piece.unwaivering==False:
                                nearest_enemy_squares[0].piece.hesitation_turns = 4  # 2 protivnicka poteza = 4 dekrementa
                            target_square.piece.mesina_turns = 4  # prati isti zivotni vek
                        else:
                            target_square.piece.active_relics.append(relic)   # SARAC, TOPUZ i eventualni ostali

                    case 2:
                        relic = game.tsar_road.get_rear()
                        if relic == RelicType.TRI_TOVARA_BLAGA and target_square.piece.is_permanent_kraljevic != True:
                            target_square.piece.active_relics.append(relic)
                            target_square.piece.promote_to_kraljevic_temporary()
                        elif relic == RelicType.TOKA_OD_CELIKA:
                            target_square.piece.active_relics.append(relic)
                            target_square.piece.armor_turns = 4 if target_square.piece.is_marko() else 2
                        elif relic == RelicType.MESINA_RUJNOG_VINA:
                            target_square.piece.active_relics.append(relic)
                            nearest_enemy_squares = game.board.get_nearest_enemy(target_square.row,target_square.col)
                            # To Do - jos samo da se ovde kasnije ubaci da se zapravo bira ona koja je najjaca figura, a da nije otporna da se mami u heuristici
                            if nearest_enemy_squares[0].piece.unwaivering==False:
                                nearest_enemy_squares[0].piece.hesitation_turns = 4  # 2 protivnicka poteza = 4 dekrementa
                            target_square.piece.mesina_turns = 4  # prati isti zivotni vek
                        else:
                            target_square.piece.active_relics.append(relic)   # SARAC, TOPUZ i eventualni ostali

                
                if target_square.piece.can_promote_to_marko():
                    print("Vasa figura je postala Marko Kraljevic - sada ima pasivnu sposobnost nepokolebljivosti.")

        game.board.decrement_relics_count()
        game.tsar_road.backfill()

    n_ary_tree.current_node.is_game_over = True
    print()
    display.print_board(game.board) # odstampamo jos jednom kada pobedi neko da se vidi konacno
    print("="*15)
    print(f"\nPobednik je {game.get_winner(game.board)}")

    reproduction_choice = input(f"\nDa li želite da pogledate Vašu igru još jednom? (y/n) >> ")
    if reproduction_choice in ["y","n","Y","N"]:
        match reproduction_choice:
            case "y" | "Y":
                print(f"\nReprodukcija:")
                n_ary_tree.traverse_the_tree()
                print(f"\nKRAJ REPORDUKCIJE!")
            case "n" | "N":
                pass

if __name__=="__main__":
    main()
