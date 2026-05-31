from board import Board
from square import Square
from piece import Piece, Player, PieceType
import move_generator as mg
import copy
from data_structures.stack import Stack

class Move:
    """
    Svaki potez je objekat ove klase i posle se koristi za heuristiku, itd.
    """
    from_row: int
    from_col: int
    to_row: int
    to_col: int
    captured: list
    
    def __init__(self, from_row, from_col, to_row, to_col, captured = None):
        self.from_row = from_row
        self.from_col = from_col
        self.to_row = to_row
        self.to_col = to_col
        self.captured = captured if captured is not None else []



class Game:
    draw_counter: int
    board: Board
    current_player: Player
    winner: Player
    undo_stack: Stack

    def __init__(self):
        self.draw_counter = 0
        self.board = Board()
        self.current_player = Player.BELI
        self.winner = None
        self.undo_stack = Stack()


    def apply_move(self, move: Move, board: Board):
        if self.is_valid_move(move, board): # type: ignore
            # Lupimo snapshot, tj. deepcopy za undo sistem:
            self.undo_stack.push(GameState(self.board, self.draw_counter, self.current_player))

            piece = board.get_piece(move.from_row, move.from_col)
            board.get_square(move.from_row, move.from_col).piece = None
            target = board.get_square(move.to_row, move.to_col)
            target.piece = piece

            for (captured_row, captured_col) in move.captured:
                board.get_square(captured_row, captured_col).piece = None

            type_before = piece.piece_type
            board.check_promotion(target)
            type_after = piece.piece_type

            promoted = (type_before != type_after)

            if move.captured or promoted:
                self.draw_counter = 0
            else:
                self.draw_counter += 1

            self.current_player = Player.CRNI if self.current_player == Player.BELI else Player.BELI

        else:
            raise Exception("Ovo nije validan potez! Pokusajte ponovo!")


    def undo(self):
        if self.undo_stack:
            state = self.undo_stack.pop()
            self.board = state.board
            self.draw_counter = state.draw_counter
            self.current_player = state.current_player


    def get_all_moves(self, player: Player, board: Board) -> list:
        """
        Vraca sve validne poteze za sve figure zadatog igraca.

        Jedenje je globalno obavezno — ako IJEDNA figura moze da skace,
        normalni potezi svih figura se odbacuju.

        Vraca listu Move objekata.
        """
        normal_moves = []
        jump_moves   = []

        for (piece, square) in board.get_all_pieces(player):
            for t in mg.get_moves(square, board):
                move = Move(
                    from_row  = square.row,
                    from_col  = square.col,
                    to_row    = t[0],
                    to_col    = t[1],
                    captured  = t[2]
                )
                if move.captured:
                    jump_moves.append(move)
                else:
                    normal_moves.append(move)

        return jump_moves if jump_moves else normal_moves


    def is_game_over(self, board: Board) -> bool:
        if board.get_all_pieces(Player.BELI)==[] or board.get_all_pieces(Player.CRNI)==[]:
            return True
        elif self.draw_counter >= 40:
            return True
        else:
            return False


    def get_winner(self, board: Board):
        if board.get_all_pieces(Player.BELI)==[]:
            return Player.CRNI
        elif board.get_all_pieces(Player.CRNI)==[]:
            return Player.BELI
        elif self.draw_counter >= 40:
            return None
        else:
            raise Exception("Do pobede nije doslo!")


    def is_valid_move(self, move: Move, board: Board):
        if not 0<=move.to_row<=7 or not 0<=move.to_col<=7:
            return False
        elif not 0<=move.from_row<=7 or not 0<=move.from_col<=7:
            return False
        elif not board.get_square(move.to_row, move.to_col).is_usable:
            return False
        else:
            return True


class GameState:
    """
    Zamrznto trenutno stanje Game-a pre odigravanja sledeceg poteza.
    Koristi se za undo stack.
    """
    draw_counter: int
    board: Board
    current_player: Player

    def __init__(self, board, draw_counter, current_player):
        self.draw_counter = draw_counter
        self.board = copy.deepcopy(board)
        self.current_player = current_player


        