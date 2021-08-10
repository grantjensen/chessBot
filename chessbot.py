import chess
import random
import chess.syzygy
import numpy as np
import sys
import dask

pawn=np.array([0,  0,  0,  0,  0,  0,  0,  0,
50, 50, 50, 50, 50, 50, 50, 50,
10, 10, 20, 30, 30, 20, 10, 10,
 5,  5, 10, 25, 25, 10,  5,  5,
 0,  0,  0, 20, 20,  0,  0,  0,
 5, -5,-10,  0,  0,-10, -5,  5,
 5, 10, 10,-20,-20, 10, 10,  5,
 0,  0,  0,  0,  0,  0,  0,  0])
pawn+=100

knight=np.array([-50,-40,-30,-30,-30,-30,-40,-50,
-40,-20,  0,  0,  0,  0,-20,-40,
-30,  0, 10, 15, 15, 10,  0,-30,
-30,  5, 15, 20, 20, 15,  5,-30,
-30,  0, 15, 20, 20, 15,  0,-30,
-30,  5, 10, 15, 15, 10,  5,-30,
-40,-20,  0,  5,  5,  0,-20,-40,
-50,-40,-30,-30,-30,-30,-40,-50])
knight+=305

bishop=np.array([-20,-10,-10,-10,-10,-10,-10,-20,
-10,  0,  0,  0,  0,  0,  0,-10,
-10,  0,  5, 10, 10,  5,  0,-10,
-10,  5,  5, 10, 10,  5,  5,-10,
-10,  0, 10, 10, 10, 10,  0,-10,
-10, 10, 10, 10, 10, 10, 10,-10,
-10,  5,  0,  0,  0,  0,  5,-10,
-20,-10,-10,-10,-10,-10,-10,-20])
bishop+=333

rook=np.array([0,  0,  0,  0,  0,  0,  0,  0,
  5, 10, 10, 10, 10, 10, 10,  5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
  0,  0,  0,  5,  5,  0,  0,  0])
rook+=563

queen=np.array([-20,-10,-10, -5, -5,-10,-10,-20,
-10,  0,  0,  0,  0,  0,  0,-10,
-10,  0,  5,  5,  5,  5,  0,-10,
 -5,  0,  5,  5,  5,  5,  0, -5,
  0,  0,  5,  5,  5,  5,  0, -5,
-10,  5,  5,  5,  5,  5,  0,-10,
-10,  0,  5,  0,  0,  0,  0,-10,
-20,-10,-10, -5, -5,-10,-10,-20])
queen+=950

king=np.array([-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-20,-30,-30,-40,-40,-30,-30,-20,
-10,-20,-20,-20,-20,-20,-20,-10,
 20, 20,  0,  0,  0,  0, 20, 20,
 20, 30, 10,  0,  0, 10, 30, 20])

kingend=np.array([[-50,-40,-30,-20,-20,-30,-40,-50],
[-30,-20,-10,  0,  0,-10,-20,-30],
[-30,-10, 20, 30, 30, 20,-10,-30],
[-30,-10, 30, 40, 40, 30,-10,-30],
[-30,-10, 30, 40, 40, 30,-10,-30],
[-30,-10, 20, 30, 30, 20,-10,-30],
[-30,-30,  0,  0,  0,  0,-30,-30],
[-50,-30,-30,-30,-30,-30,-30,-50]])


def evaluate_board(board):
    val = 0
    i=-1
    state=board.fen()
    for char in state:
        i+=1
        if char == " ":
            return val
        elif char == '/':
            i-=1
        elif char.isnumeric():
            i+=int(char)-1
            continue
        elif char == 'p':
            val-=pawn[i]
        elif char == 'P':
            val+=pawn[63-i]
        elif char == 'n':
            val-=knight[i]
        elif char == 'N':
            val+=knight[63-i]
        elif char == 'b':
            val-=bishop[i]
        elif char == 'B':
            val+=bishop[63-i]
        elif char == 'r':
            val-=rook[i]
        elif char == 'R':
            val+=rook[63-i]
        elif char == 'q':
            val-=queen[i]
        elif char == 'Q':
            val+=queen[63-i]
        elif char == 'k':
            val-=king[i]
        elif char == 'K':
            val+=king[63-i]


def num_pieces(board):
    s=board.fen().split()[0]
    return sum(c.isalpha() for c in s)

def evaluate(prevdict, prevval, move):
#     if(num_pieces(board))<=6:
#         wdl=tablebase.probe_wdl(board)
#         turn=board.turn
#         if((turn==True and wdl==2) or (turn==False and wdl==-2)):
#             # Tablebase win
#             return 20000
#         elif(wdl==2 or wdl==-2):
#             # Tablebase loss
#             return -20000
#         else:
#             # Tablebase draw
#             return 0
    evalin=prevval
    attack_piece=prevdict[move.from_square].symbol()
    if move.to_square in prevdict.keys():
        captured_piece=prevdict[move.to_square].symbol()
        if captured_piece == 'p':
            prevval+=pawn[63-move.to_square]
        elif captured_piece == 'P':
            prevval-=pawn[move.to_square]
        elif captured_piece == 'n':
            prevval+=knight[63-move.to_square]
        elif captured_piece == 'N':
            prevval-=knight[move.to_square]
        elif captured_piece == 'b':
            prevval+=bishop[63-move.to_square]
        elif captured_piece == 'B':
            prevval-=bishop[move.to_square]
        elif captured_piece == 'r':
            prevval+=rook[63-move.to_square]
        elif captured_piece == 'R':
            prevval-=rook[move.to_square]
        elif captured_piece == 'q':
            prevval+=queen[63-move.to_square]
        elif captured_piece == 'Q':
            prevval-=queen[move.to_square]
        elif captured_piece == 'k':
            prevval+=king[63-move.to_square]
        elif captured_piece == 'K':
            prevval-=king[move.to_square]
    promote=move.promotion
    if promote is not None:
        if attack_piece == 'p':
            prevval+=pawn[move.from_square]
            if promote==2:
                prevval-=knight[move.to_square]
            elif promote==3:
                prevval-=bishop[move.to_square]
            elif promote==4:
                prevval-=rook[move.to_square]
            elif promote==5:
                prevval-=queen[move.to_square]
            else:
                print("Promotion error")
        elif attack_piece == 'P':
            prevval-=pawn[63-move.from_square]
            if promote==2:
                prevval+=knight[63-move.to_square]
            elif promote==3:
                prevval+=bishop[63-move.to_square]
            elif promote==4:
                prevval+=rook[63-move.to_square]
            elif promote==5:
                prevval+=queen[63-move.to_square]
            else:
                print("Promotion error")
        
    if attack_piece == 'p':
        prevval-=pawn[move.to_square]
        prevval+=pawn[move.from_square]
    elif attack_piece == 'P':
        prevval-=pawn[63-move.from_square]
        prevval+=pawn[63-move.to_square]
    elif attack_piece == 'n':
        prevval-=knight[move.to_square]
        prevval+=knight[move.from_square]
    elif attack_piece == 'N':
        prevval-=knight[63-move.from_square]
        prevval+=knight[63-move.to_square]
    elif attack_piece == 'b':
        prevval-=bishop[move.to_square]
        prevval+=bishop[move.from_square]
    elif attack_piece == 'B':
        prevval-=bishop[63-move.from_square]
        prevval+=bishop[63-move.to_square]
    elif attack_piece == 'r':
        prevval-=rook[move.to_square]
        prevval+=rook[move.from_square]
    elif attack_piece == 'R':
        prevval-=rook[63-move.from_square]
        prevval+=rook[63-move.to_square]
    elif attack_piece == 'q':
        prevval-=queen[move.to_square]
        prevval+=queen[move.from_square]
    elif attack_piece == 'Q':
        prevval-=queen[63-move.from_square]
        prevval+=queen[63-move.to_square]
    elif attack_piece == 'k':
        prevval-=king[move.to_square]
        prevval+=king[move.from_square]
    elif attack_piece == 'K':
        prevval-=king[63-move.from_square]
        prevval+=king[63-move.to_square]
    return prevval


def minimax(currdepth, maxdepth, board, alpha, beta, prevval, move):
    #global mtime    
    if board.outcome() is not None:
        winner=board.outcome().winner
        if winner is None:
            return 0
        elif(winner==True):
            return 20000
        else:
            return -20000
    if currdepth==maxdepth:
        return prevval
    
    prevdict=board.piece_map()
    moves=np.array(list(board.legal_moves))
    vals=np.zeros(len(moves), dtype='int')
    for i in range(len(moves)):
        vals[i]=evaluate(prevdict, prevval, moves[i])
    #ms=time.time()
    ordering=np.argsort(vals)
    #mtime+=time.time()-ms
    vals=np.take(vals,ordering)
    moves=np.take(moves,ordering)
    
    
    
    
    

    if board.turn:  # white player
        moves=np.flip(moves)
        vals=np.flip(vals)
        best = -20000
        index_max=-1
        for i in range(len(moves)):
            board.push(moves[i])
            val = minimax(currdepth+1, maxdepth, board, alpha, beta, vals[i], moves[i])
            board.pop()
            if best<val:
                best=val
                index_max=i
                alpha=max(alpha,best)
                if beta<=alpha:
                    break
            
        if currdepth==0:
            return [best, moves[index_max]]
        else:
            return best
    else:  # Black player
        best=20000
        index_min=-1
        for i in range(len(moves)):
            board.push(moves[i])
            val = minimax(currdepth+1, maxdepth, board, alpha, beta, vals[i], moves[i])
            board.pop()
            if val<best:
                index_min=i
                best=val
                beta=min(beta,best)
                if beta<=alpha:
                    break
        if currdepth==0:
            return [best, moves[index_min]]
        else:
            return best
        
        
def flip(boardstr):
    l = boardstr.split("\n")
    reverse = "\n".join(l[::-1])
    return reverse

        
def play(depth):
    color=None
    while color!='w' and color!='b':
        color=input("Welcome to Grant's chess program!\nChoose a color.\nEnter w or b: ")
    board=chess.Board()
    move_counter=1
    if color == 'b':
        while board.outcome() is None:
            comp_move=minimax(0,depth,board,-40000,40000, evaluate_board(board), None)[1]
            print(str(move_counter)+". "+board.san(comp_move)+"\n")
            board.push(comp_move)
            print(flip(chess.BaseBoard(board.board_fen()).unicode(invert_color=True)))
            print("")
            if (board.outcome() is not None):
                break
            while True:
                player_move=input(str(move_counter)+"... ")
                try:
                    board.push_san(player_move)
                    break
                except:
                    print(player_move+" is not a valid move.\n")
            print(flip(chess.BaseBoard(board.board_fen()).unicode(invert_color=True)))
            print("")
            move_counter+=1
    if color == 'w':
        print(chess.BaseBoard(board.board_fen()).unicode(invert_color=True))
        print("")
        while board.outcome() is None:
            while True:
                player_move=input(str(move_counter)+". ")
                try:
                    board.push_san(player_move)
                    break
                except:
                    print(player_move+" is not a valid move.\n")
            print(chess.BaseBoard(board.board_fen()).unicode(invert_color=True))
            print("")
            if(board.outcome() is not None):
                break
            comp_move=minimax(0,depth,board,-40000,40000, evaluate_board(board), None)[1]
            print(str(move_counter)+"... "+board.san(comp_move)+"\n")
            board.push(comp_move)
            print(chess.BaseBoard(board.board_fen()).unicode(invert_color=True))
            print("")
            move_counter+=1
    print(board.outcome())
            