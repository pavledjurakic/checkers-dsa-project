from __future__ import annotations # Tree Node warning resolution
from board import *
from game import *
import display, time


class N_Ary_Tree():

    def __init__(self, board: Board):
        self.root = Tree_Node(None, board)
        self.current_node = self.root
        
    def add_next_move(self, move: Move, board: Board):
        new_node = Tree_Node(move, board, self.current_node)
        self.current_node.children.append(new_node)
        self.current_node = new_node
    
    def traverse_the_tree(self):
        traverse_the_node(self.root)

#============================================================================================================

def display_node(node):
    if node.move is None:
        print("Početno stanje:")
    else:
        print(f"Potez: ({node.move.from_row},{node.move.from_col}) -> ({node.move.to_row},{node.move.to_col})")
    display.print_board(node.board_state)
    time.sleep(1)


def traverse_the_node(node):
    current = node

    while current is not None:
        display_node(current)

        if current.is_game_over:
            break

        if current.children:
            # idi na prvo dete
            current = current.children[0]
        else:
            # list koji nije game_over - penjemo se gore trazeci neposecenog siblinga
            while current is not None:
                parent = current.parent
                if parent is None:
                    return  # dosli smo do korena, gotovo
                idx = parent.children.index(current)
                # prikazujemo undo korak
                print("===== UNDO =====")
                display_node(parent)
                if idx + 1 < len(parent.children):
                    # nasli smo neposecenog siblinga - nastavljamo odatle
                    current = parent.children[idx + 1]
                    break
                current = parent  # nastavi penjanje


#==================================================================================


class Tree_Node():
    move: Move
    board_state: Board
    parent: Tree_Node
    children: list[Tree_Node]

    def __init__(self, move, board, parent=None, is_game_over = False):
        self.move = move
        self.board_state = copy.deepcopy(board)
        self.parent = parent
        self.children = []
        self.is_game_over = is_game_over
    