from board import Board
from square import Square
from piece import Piece, Player, PieceType
import move_generator as mg
import copy
from tsar_road import *
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
    
    def __init__(self, from_row, from_col, to_row, to_col, captured=None, relics_used=None):
        self.from_row = from_row
        self.from_col = from_col
        self.to_row = to_row
        self.to_col = to_col
        self.captured = captured if captured is not None else []
        self.relics_used = relics_used if relics_used is not None else frozenset()



class Game:
    draw_counter: int
    board: Board
    current_player: Player
    winner: Player
    undo_stack: Stack
    tsar_road: TsarRoad
    ai_player: Player
    human_player: Player

    def __init__(self):
        self.draw_counter = 0
        self.board = Board()
        self.current_player = Player.BELI
        self.winner = None
        self.undo_stack = Stack()
        self.tsar_road = TsarRoad()
        self.ai_player = None
        self.human_player = None


    def apply_move(self, move: Move, board: Board):
        if self.is_valid_move(move, board): # type: ignore
            # Lupimo snapshot, tj. deepcopy za undo sistem:
            self.undo_stack.push(GameState(self.board, self.draw_counter, self.current_player, self.tsar_road))

            # Topuz slucaj: figura uskace na enemy square, pa mora captured prvo da se ukloni
            for (captured_row, captured_col) in move.captured:
                board.get_square(captured_row, captured_col).piece = None

            piece = board.get_piece(move.from_row, move.from_col)
            board.get_square(move.from_row, move.from_col).piece = None
            target = board.get_square(move.to_row, move.to_col)
            target.piece = piece

            # Ukloni iskoriscene relikvije (Topuz, Sarac - svaki se koristi samo jednom)
            for relic in move.relics_used:
                if relic in piece.active_relics:
                    piece.active_relics.remove(relic)

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
            self.tsar_road = state.tsar_road
            return True
        return False


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
                    from_row    = square.row,
                    from_col    = square.col,
                    to_row      = t[0],
                    to_col      = t[1],
                    captured    = t[2],
                    relics_used = t[3]
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
            self.winner = Player.CRNI
            return self.winner
        elif board.get_all_pieces(Player.CRNI)==[]:
            self.winner = Player.BELI
            return self.winner
        elif self.draw_counter >= 40:
            return "NERESENO"
        else:
            if self.winner is not None:
                return self.winner
            else:
                raise Exception("Do pobede nije doslo - nepredvidjen slucaj!")


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
    tsar_road: TsarRoad

    def __init__(self, board, draw_counter, current_player, tsar_road):
        self.draw_counter = draw_counter
        self.board = copy.deepcopy(board)
        self.current_player = current_player
        self.tsar_road = copy.deepcopy(tsar_road)

        