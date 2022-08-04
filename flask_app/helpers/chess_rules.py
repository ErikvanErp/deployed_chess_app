
#******************************************************************************
# 
# This module contains pure functions that encode the rules of the game
# - validation of moves by various pieces
# - verification of check and check-mate
#
#******************************************************************************

# a global variable that is CONSTANT
pieces = {
            '0': (None, None, " "),
            '1': ("w", "k", u'\u2654'), 
            '2': ("w", "q", u'\u2655'), 
            '3': ("w", "b", u'\u2657'), 
            '4': ("w", "n", u'\u2658'), 
            '5': ("w", "r", u'\u2656'), 
            '6': ("w", "p", u'\u2659'), 
            '7': ("b", "k", u'\u265A'), 
            '8': ("b", "q", u'\u265B'), 
            '9': ("b", "b", u'\u265D'), 
            'A': ("b", "n", u'\u265E'), 
            'B': ("b", "r", u'\u265C'), 
            'C': ("b", "p", u'\u265F')
        }

#******************************************************************************
#
# is_valid_move:
# checks whether a proposed move is valid,
# For Castling and En Passant Capture of a pawn,
# previous moves need to be considered.
#
# this is where the rules of chess are coded
#******************************************************************************

def is_valid_move(game_state, *from_to):
    (from_row, from_col, to_row, to_col) = from_to
    vector = (to_row - from_row, to_col - from_col)
    
    if not general_rules(game_state.board, from_to):
        return False
    
    # color: the color of the piece on the "from" tile
    # color_to: the color of a piece on the tile we want to move to
    # if there is no piece there, color_to is None
    color, type, ucode = pieces[game_state.board[from_row][from_col]]
    color_to, type_to, ucode_to = pieces[game_state.board[to_row][to_col]]

    # test if the proposed move results in "check"
    # 1. copy the board
    new_board = [[tile for tile in row] for row in game_state.board]
    # 2. make the move on new_board
    moving_piece = new_board[from_row][from_col]
    new_board[to_row][to_col] = moving_piece
    new_board[from_row][from_col] = '0'
    # 3. test whether player with color is check on new_board
    if is_check(new_board, color):
        return False

    # if the move does not result in a check situation,
    # see if it is valid.

    # castling is represented as a move of the king
    if type == "k":
        if from_to in [(0, 3, 0, 1), (0, 3, 0, 5), (7, 3, 7, 1), (7, 3, 7, 5)] and castling_rules(game_state, from_to):
            return True
        elif king_rules(game_state.board, from_to):
            return True
        else:
            return False

    elif type == "n":
        if knight_rules(game_state.board, from_to):
            return True
        else:
            return False

    elif type == "p":
        return pawn_rules(game_state, from_to)

    elif type in ["q", "r", "b"]:
        if queen_rook_bishop_rules(game_state.board, from_to, type):
            return True
        else:
            return False


# general_rules is called by all rules for moving a piece
def general_rules(board, move):
    from_row, from_col, to_row, to_col = move

    # is the move in range
    if from_row not in range(8):
        return False 
    if from_col not in range(8):
        return False 
    if to_row not in range(8):
        return False 
    if to_col not in range(8):
        return False 
    
    # the "from" position is not empty
    if board[from_row][from_col] == '0':
        return False

    # you cannot capture your own piece
    color, type, ucode = pieces[board[from_row][from_col]]
    color_to, type_to, ucode_to = pieces[board[to_row][to_col]]

    if color == color_to:
        return False

    return True

#  
#  The rules for moving various pieces (excl pawn)
#  All these functions call general_rules
#  

def king_rules(board, move):
        from_row, from_col, to_row, to_col = move
        vector = (to_row - from_row, to_col - from_col)

        if not general_rules(board, move):
            return False

        if vector in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1, -1), (1, 0), (1, 1)]:
            # make a copy of board and move king on new_board
            color = pieces[board[from_row][from_col]][0]

            new_board = [[tile for tile in row] for row in board]
            new_board[to_row][to_col] = '1' if color == 'w' else '7'
            new_board[from_row][from_col] = '0'

            # make sure king is not check-mate after proposed move
            if is_check(new_board, color):
                return False
            else:
                return True
        else:
            return False
    
def knight_rules(board, move):
    from_row, from_col, to_row, to_col = move
    vector = (to_row - from_row, to_col - from_col)

    if not general_rules(board, move):
        return False

    if vector in [(1,2), (1,-2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2,-1)]:
        return True
    else:
        return False

# rules for queen, rook, bishop
# the pieces with simple straight or diagonal motion
def queen_rook_bishop_rules(board, move, type):
    from_row, from_col, to_row, to_col = move
    vector = (to_row - from_row, to_col - from_col)

    if not general_rules(board, move):
        return False

    # queen, bishop, rook follow the rules of diagonal or straight motion
    # the move is allowed if 
    # 1. it is in the right direction for the piece
    # 2. there are no obstacles between "from" and "to"

    # 1. check that the piece moves in the right direction
    is_straight = True if vector[0] == 0 or vector[1] == 0 else False
    is_diagonal = True if vector[0] == vector[1] or vector[0] == - vector[1] else False

    if type == "q" and not (is_straight or is_diagonal):
        return False
    if type == "r" and not is_straight:
        return False
    if type == "b" and not is_diagonal:
        return False

    # 2. check for obstacles

    # how many steps are we moving?
    # if only 1 step, we are done.
    how_many = max(abs(vector[0]), abs(vector[1]))
    if how_many < 2:
        return True

    # in which direction are we moving?
    unit = [0,0]

    if vector[0] > 0:
        unit[0] = +1
    elif vector[0] < 0:
        unit[0] = -1
    else:
        unit[0] = 0

    if vector[1] > 0:
        unit[1] = +1
    elif vector[1] < 0:
        unit[1] = -1
    else:
        unit[1] = 0

    # now check all intermediate positions
    # if any piece is in the way, the move is invalid
    for i in range(1, how_many):
        if not board[from_row + unit[0] * i][from_col + unit[1] * i] == "0":
            return False 

    # if the direction is correct, and no obstacles are found, the move is valid
    return True


# validation of moves by the pawn
# For en passant capture we need to check the previous move
def pawn_rules(game_state, from_to):
    from_row, from_col, to_row, to_col = from_to
    vector = (to_row - from_row, to_col - from_col)
    
    color, type, ucode = pieces[game_state.board[from_row][from_col]]
    color_to, type_to, ucode_to = pieces[game_state.board[to_row][to_col]]

    # vertical direction of motion and starting row depend on color
    forward = 1 if color == "w" else -1
    start_row = 1 if color == "w" else 6

    # for each of 4 possible vectors allowed by a pawn, check if they are valid

    # move 1 forward to an empty spot
    if vector == (forward, 0):
        if game_state.board[from_row + forward][from_col] == "0":
            return True
        else:
            return False
    
    # move 2 forward; only allowed from starting position
    elif vector == (2 * forward,0) and from_row == start_row:
        if game_state.board[from_row + forward][from_col] == "0" and game_state.board[from_row + 2 * forward][from_col] == "0":
            return True
        else: 
            return False

    # capture of a piece
    elif vector in [(forward, 1), (forward, -1)]:
        # an ordinary capture
        if color_to and color != color_to:
            return True
        # en passant capture of pawn
        else:
            if ((not color_to) and color == "w" 
                    and from_row == 4  
                    and game_state.last_piece_moved == 'C'
                    and game_state.last_move[0] == 6
                    and game_state.last_move[1] == to_col
                    and game_state.last_move[2] == 4):
                return True
            elif ((not color_to) and color == "b" 
                    and from_row == 3  
                    and game_state.last_piece_moved == '6'
                    and game_state.last_move[0] == 1
                    and game_state.last_move[1] == to_col
                    and game_state.last_move[2] == 3):
                return True
            else:
                return False


# validation of castling 
# represented as a move of the king, but also involves a rook
# for validation of castling we need to check past moves
# the king and rook involved in castling may not have moved before
def castling_rules(game_state, from_to):

    if (from_to == (0, 3, 0, 1) and game_state.board[0][0:4] == ['5','0','0','1']
            and not game_state.white_king_moved and not game_state.white_rook_0_moved):
        return True 
    elif (from_to == (7, 3, 7, 1) and game_state.board[7][0:4] == ['B','0','0','7']
            and not game_state.black_king_moved and not game_state.black_rook_0_moved):
        return True 
    elif (from_to == (0, 3, 0, 5) and game_state.board[0][4:8] == ['1','0','0','0','5']
            and not game_state.white_king_moved and not game_state.white_rook_7_moved):
        return True 
    elif (from_to == (7, 3, 7, 5) and game_state.board[7][4:8] == ['7','0','0','0','B']
            and not game_state.black_king_moved and game_state.black_rook_7_moved):
        return True 
    else:
        return False



#
#  Functions for check and check-mate
#  These functions rely on the rules for moving pieces
#

# is king with color check
# i.e. is the king under attack by opponent
def is_check(board, color):

    # find the king
    for i in range(8):
        for j in range(8):
            if ((color == "w" and board[i][j] == '1') 
                or (color == "b" and board[i][j] == '7')):
                king = (i, j)

    # print(f"king {king[0]}, {king[1]}")
    # return True from the loop as soon as 
    # an opponent's piece is found that attacks the king
    opponent = "b" if color == "w" else "w"
    # print(f"opponent {opponent}")

    # check all 64 tiles (other than the king in question)
    for i in range(8):
        for j in range(8):
            # print(f"tile: i {i} j {j}")
            if (i, j) == king:
                continue
            tile = board[i][j]
            # print(f"piece {board[i][j]}")
            # if the tile contains a piece with the opponent's color
            if pieces[tile][0] == opponent: 
                # check whether it can move to king
                move = (i, j, king[0], king[1])
                type = pieces[tile][1]
                # print(f"type {type}")
                # don't use king_rules to avoid circularity
                # king_rules needs to call is_check
                # note that a king can not be "checked" by another king
                # but we need to test this for the purpose of check_mate
                if type == "k" and i - king[0] in [-1,0,1] and j - king[1] in [-1,0,1]:
                    return True
                elif type == "n" and knight_rules(board, move):
                    return True
                #  The simple rules for capture of the king by pawns are hardcoded here
                elif type == "p":
                    forward = 1 if opponent == "w" else -1
                    if king[0] == i + forward and (king[1] == j + 1 or king[1] == j - 1):
                        return True
                elif type in ["q", "r", "b"] and queen_rook_bishop_rules(board, move, type):
                    return True

    # if no attackers were found, return False
    return False

# is king with color check mate 
# relies on is_check

# there is one situation where check_mate depends on previous move:
# if en passant capture can get us out of check
# this is why we have to import the game_state, and not just the board
def is_check_mate(game_state, color):

    board = game_state.board
    print(f"board {board}")

    # if not check, then not check mate
    if not is_check(board, color):
        print("not check on first test")
        return False

    # find the king
    for i in range(8):
        for j in range(8):
            if ((color == "w" and board[i][j] == '1') # white king 
                or (color == "b" and board[i][j] == '7')): # black king
                king = (i, j)

    print(f"king {king[0]} {king[1]}")
    # test whether any valid move is available 
    # to escape the check
    for from_row in range(8):
        for from_col in range(8):
            # find all pieces of king's color
            if pieces[board[from_row][from_col]][0] == color:
                print(pieces[board[from_row][from_col]][2])
                for to_row in range(8):
                    for to_col in range(8):
                        # now test whether this piece can move from ... to ...
                        if is_valid_move(game_state, from_row, from_col, to_row, to_col):
                            print(f"is valid move from {from_row} {from_col} to {to_row} {to_col}")
                            # if the move is valid, test if it fixes the check 
                            new_board = [[tile for tile in row] for row in board]
                            new_board[to_row][to_col] = board[from_row][from_col]
                            new_board[from_row][from_col] = '0'
                            # if the move results in a new_board where king is not check
                            # return False (not check mate)
                            if not is_check(new_board, color):
                                print("is not check")
                                return False

    # if no move to safety is found, return True (check-mate)
    return True



