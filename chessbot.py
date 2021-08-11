import chess
import chess.syzygy
import numpy as np
import sys
from chess.polyglot import zobrist_hash as zhash
import time

TT=[None]*0xFFFF


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
  0,  -10,  0,  5,  5,  0,  -10,  0])
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
            if board.turn:
                return val
            else:
                return -val
        elif char == '/':
            i-=1
        elif char.isnumeric():
            i+=int(char)-1
            continue
        elif char == 'p':
            val-=pawn[63-i]
        elif char == 'P':
            val+=pawn[i]
        elif char == 'n':
            val-=knight[63-i]
        elif char == 'N':
            val+=knight[i]
        elif char == 'b':
            val-=bishop[63-i]
        elif char == 'B':
            val+=bishop[i]
        elif char == 'r':
            val-=rook[63-i]
        elif char == 'R':
            val+=rook[i]
        elif char == 'q':
            val-=queen[63-i]
        elif char == 'Q':
            val+=queen[i]
        elif char == 'k':
            val-=king[63-i]
        elif char == 'K':
            val+=king[i]


def evaluate(prevdict, prevval, move, board):
    who_to_move = not board.turn
    if who_to_move:
        prevval=-prevval
    if board.is_en_passant(move):
        if prevdict[move.from_square].symbol()=='p':  #black capture
            prevval-=pawn[move.to_square]
            prevval+=pawn[move.from_square]
            prevval-=pawn[63-(move.to_square+8)]
        else:
            prevval-=pawn[63-move.from_square]
            prevval+=pawn[63-move.to_square]
            prevval+=pawn[move.to_square-8]
        if who_to_move:#white
            return prevval
        else:
            return -prevval
    attack_piece=prevdict[move.from_square].symbol()
    if move.to_square in prevdict.keys():
        captured_piece=prevdict[move.to_square].symbol()
        if captured_piece == 'p':
            prevval+=pawn[move.to_square]
        elif captured_piece == 'P':
            prevval-=pawn[63-move.to_square]
        elif captured_piece == 'n':
            prevval+=knight[move.to_square]
        elif captured_piece == 'N':
            prevval-=knight[63-move.to_square]
        elif captured_piece == 'b':
            prevval+=bishop[move.to_square]
        elif captured_piece == 'B':
            prevval-=bishop[63-move.to_square]
        elif captured_piece == 'r':
            prevval+=rook[move.to_square]
        elif captured_piece == 'R':
            prevval-=rook[63-move.to_square]
        elif captured_piece == 'q':
            prevval+=queen[move.to_square]
        elif captured_piece == 'Q':
            prevval-=queen[63-move.to_square]
        elif captured_piece == 'k':
            prevval+=king[move.to_square]
        elif captured_piece == 'K':
            prevval-=king[63-move.to_square]
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
    if who_to_move:#white
        return prevval
    else:
        return -prevval

def updatePieceMap(piece_map, move, board):
    if move==None:
        return piece_map
    promote=move.promotion
    if board.is_en_passant(move):
        piece_map[move.to_square]=piece_map[move.from_square]
        piece_map.pop(move.from_square)
        if piece_map[move.to_square].symbol()=='p':
            piece_map.pop(move.to_square+8)
        else:
            piece_map.pop(move.to_square-8)
        return piece_map
    if board.is_castling(move):
        if move.to_square==6:#white kingside castle
            piece_map[5]=piece_map[7]
            piece_map.pop(7)
        elif move.to_square==2:# white queenside
            piece_map[3]=piece_map[0]
            piece_map.pop(0)
        elif move.to_square==62:# black kingside
            piece_map[61]=piece_map[63]
            piece_map.pop(63)
        else:#black queenside
            piece_map[59]=piece_map[56]
            piece_map.pop(56)
            
    if promote is None:
        piece_map[move.to_square]=piece_map[move.from_square]
        piece_map.pop(move.from_square)
        return piece_map
    else:
        piece_map.pop(move.from_square)
        if promote==5:
            piece_map[move.to_square]=chess.Piece.from_symbol('Q')
        if promote==4:
            piece_map[move.to_square]=chess.Piece.from_symbol('R')
        if promote==3:
            piece_map[move.to_square]=chess.Piece.from_symbol('B')
        if promote==2:
            piece_map[move.to_square]=chess.Piece.from_symbol('N')
        return piece_map

def minimax(depth, board, alpha, beta, prevval, move, piece_map, start_time, time_to_run):
    if board.outcome() is not None:
        winner=board.outcome().winner
        if winner is None:
            return [0, None, False]
        elif(winner==True):
            if board.turn:
                return [20000, None, False]
            else:
                return [-20000, None, False]
        else:
            if board.turn:          
                return [-20000, None, False]
            else:
                return [20000, None, False]
    if depth==0:
        return [prevval, None, False]
    origalpha=alpha
    currzorbrist=zhash(board)
    hashval=currzorbrist%0xFFFF
    if TT[hashval] is not None:
        if TT[hashval].zorbrist==currzorbrist and TT[hashval].depth>=depth:
            if TT[hashval].exact:
                return [TT[hashval].val, chess.Move.from_uci(TT[hashval].best_move), 1]
            if TT[hashval].alphaflag and alpha<TT[hashval].val:
                alpha=TT[hashval].val
            if TT[hashval].betaflag and beta>TT[hashval].val:
                beta=TT[hashval].val
            if(alpha>=beta):
                return [TT[hashval].val, chess.Move.from_uci(TT[hashval].best_move), 1]
    bestval=-20000
    completed=True
    best_move=None
    pmc=piece_map.copy()
    for i, move in enumerate(board.legal_moves):
        tmpval=evaluate(pmc,prevval,move, board)
        piece_map=updatePieceMap(pmc.copy(), move, board)
        
        board.push(move)
        if i>0:
            currval=-minimax(depth-1, board, -alpha-1, -alpha, tmpval,move, piece_map, start_time, time_to_run)[0]
            if alpha<currval and currval < beta:
                currval=-minimax(depth-1,board, -beta,-currval,tmpval,move,piece_map, start_time, time_to_run)[0]
        else:
            currval=-minimax(depth-1,board,-beta,-alpha,tmpval,move,piece_map, start_time, time_to_run)[0]
        board.pop()
        if(time.time()-start_time>=time_to_run): 
            completed=False
            break
        if(bestval<currval):
            bestval=currval
            best_move=move
            if bestval>=beta:
                break
        if alpha<bestval:
            alpha=bestval
    if(completed):
        enterTT(board, origalpha, beta, -bestval, best_move.uci(), depth)
    return [bestval, best_move, completed]


def choose_move(board, time_to_run):
    start_time=time.time()
    val=evaluate_board(board)
    TT=[None]*0xFFFF
    for depth in range(1,10):
        out=minimax(depth, board, -40000, 40000, val, None, board.piece_map(), start_time, time_to_run)
        if out[2]:
            best_move=out[1]
        if(time.time()-start_time>=time_to_run):
            break
    return best_move



def enterTT(board, alpha, beta, val, best_move, depth):
    zorbrist=zhash(board)
    hashval=zorbrist%0xFFFF
    if(val<=alpha):
        betaflag=True
        alphaflag=False
        exact=False
    elif(val>=beta):
        alphaflag=True
        betaflag=False
        exact=False
    else:
        alphaflag=False
        betaflag=False
        exact=True
    entry=TTEntry(zorbrist, depth, -val, alphaflag, betaflag, exact, best_move)
    TT[hashval]=entry
    
    

def flip(boardstr):
    l = boardstr.split("\n")
    reverse = "\n".join(l[::-1])
    return reverse



        
def play(time_to_run):
    color=None
    while color!='w' and color!='b':
        color=input("Welcome to Grant's chess program!\nChoose a color.\nEnter w or b: ")
    board=chess.Board()
    move_counter=1
    if color == 'b':
        while board.outcome() is None:
            comp_move=choose_move(board, time_to_run)
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
            comp_move=choose_move(board, time_to_run)
            print(str(move_counter)+"... "+board.san(comp_move)+"\n")
            board.push(comp_move)
            print(chess.BaseBoard(board.board_fen()).unicode(invert_color=True))
            print("")
            move_counter+=1
    print(board.outcome())
            
        
class TTEntry:
    def __init__(self, zorbrist, depth, val, alphaflag, betaflag, exact, best_move):
        self.zorbrist = zorbrist #Full hash
        self.depth = depth
        self.val = val
        self.alphaflag = alphaflag
        self.betaflag = betaflag
        self.exact = exact
        self.best_move = best_move  # uci format
        
if __name__ == "__main__":
    if len(sys.argv)!=2:
        print("Incorrect number of args")
    else:
        play(int(sys.argv[1]))