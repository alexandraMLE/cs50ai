"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy
import copy


X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    if board == initial_state():
        return X
    
    X_count = 0
    O_count = 0
    for row in board:
        for cells in board:
            X_count += row.count(X)
            O_count += row.count(O)

    if X_count > O_count:
        return O
    elif O_count == X_count and not terminal(board):
        return X
    else:
        return None


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board. set possible actions as an empty set initially
    (i, j) range values range(3) == 0,1,2
    """
    valid_actions = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                valid_actions.add((i, j))
    return valid_actions
    

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    r_board = copy.deepcopy(board)
    if action not in actions(board):
        raise Exception("space occupied")
    else:
        r_board = copy.deepcopy(board)
        r_board[action[0]][action[1]] = player(board)
        return r_board


def winner(board):
    """
    Returns the winner of the game, if there is one. 
    Note the space of columns, check the rows, i, and columns, j, and diagonals
    """
    columns = [] 
    for row in board:
        X_counter = row.count(X)
        O_counter = row.count(O)
        if X_counter == 3:
            return X
        if O_counter == 3:
            return O

    for j in range(len(board)):
        column = [row[j] for row in board]
        columns.append(column)

    for j in columns:
        X_counter = j.count(X)
        O_counter = j.count(O)
        if X_counter == 3:
            return X
        if O_counter == 3:
            return O

    if board[0][0] == O and board[1][1] == O and board[2][2] == O:
        return O
    if board[0][2] == O and board[1][1] == O and board[2][0] == O:
        return O
    if board[0][0] == X and board[1][1] == X and board[2][2] == X:
        return X
    if board[0][2] == X and board[1][1] == X and board[2][0] == X:
        return X
    
    return None

                
def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    Assuming utility will only be called on a board if terminal(board) True
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0 


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    v = -math.inf for current.player X because returning max
    """
    if terminal(board):
        return None
    
    if player(board) == X:
        best = -math.inf
        optimal_action = None
        
        for action in actions(board):
            min_v = min_value(result(board, action))
            if min_v > best:
                best = min_v
                optimal_action = action

        return optimal_action
    
    elif player(board) == O:
        best = math.inf
        optimal_action = None

        for action in actions(board):
            max_v = max_value(result(board, action))
            if max_v < best:
                best = max_v
                optimal_action = action
        
        return optimal_action


def max_value(board): # recursive

    if terminal(board):
        return utility(board)

    optimal = -math.inf

    for action in actions(board):
        optimal = max(optimal, min_value(result(board, action)))

    return optimal


def min_value(board):

    if terminal(board):
        return utility(board)

    optimal = math.inf

    for action in actions(board):
        optimal = min(optimal, max_value(result(board, action)))

    return optimal
    
    optimal = float(-math.inf)
    for action in actions(board):
        best = min_value(result(board, action))
        if best > optimal:
            optimal = best
            if optimal == 1:
                return optimal
    return optimal

