import chess
import random
import chess.syzygy
import numpy as np

pawn=np.array([[ 0,  0,  0,  0,  0,  0,  0,  0],
[50, 50, 50, 50, 50, 50, 50, 50],
[10, 10, 20, 30, 30, 20, 10, 10],
[5,  5, 10, 25, 25, 10,  5,  5],
[0,  0,  0, 20, 20,  0,  0,  0],
[5, -5,-10,  0,  0,-10, -5,  5],
[5, 10, 10,-20,-20, 10, 10,  5],
[0,  0,  0,  0,  0,  0,  0,  0]])
pawn+=100

knight=np.array([[-50,-40,-30,-30,-30,-30,-40,-50],
[-40,-20,  0,  0,  0,  0,-20,-40],
[-30,  0, 10, 15, 15, 10,  0,-30],
[-30,  5, 15, 20, 20, 15,  5,-30],
[-30,  0, 15, 20, 20, 15,  0,-30],
[-30,  5, 10, 15, 15, 10,  5,-30],
[-40,-20,  0,  5,  5,  0,-20,-40],
[-50,-40,-30,-30,-30,-30,-40,-50]])
knight+=305

bishop=np.array([[-20,-10,-10,-10,-10,-10,-10,-20],
[-10,  0,  0,  0,  0,  0,  0,-10],
[-10,  0,  5, 10, 10,  5,  0,-10],
[-10,  5,  5, 10, 10,  5,  5,-10],
[-10,  0, 10, 10, 10, 10,  0,-10],
[-10, 10, 10, 10, 10, 10, 10,-10],
[-10,  5,  0,  0,  0,  0,  5,-10],
[-20,-10,-10,-10,-10,-10,-10,-20]])
bishop+=333

rook=np.array([[0,  0,  0,  0,  0,  0,  0,  0],
[5, 10, 10, 10, 10, 10, 10,  5],
[-5,  0,  0,  0,  0,  0,  0, -5],
[-5,  0,  0,  0,  0,  0,  0, -5],
[-5,  0,  0,  0,  0,  0,  0, -5],
[-5,  0,  0,  0,  0,  0,  0, -5],
[-5,  0,  0,  0,  0,  0,  0, -5],
[0,  0,  0,  5,  5,  0,  0,  0]])
rook+=563

queen=np.array([[-20,-10,-10, -5, -5,-10,-10,-20],
[-10,  0,  0,  0,  0,  0,  0,-10],
[-10,  0,  5,  5,  5,  5,  0,-10],
[-5,  0,  5,  5,  5,  5,  0, -5],
[0,  0,  5,  5,  5,  5,  0, -5],
[-10,  5,  5,  5,  5,  5,  0,-10],
[-10,  0,  5,  0,  0,  0,  0,-10],
[-20,-10,-10, -5, -5,-10,-10,-20]])
queen+=950

king=np.array([[-30,-40,-40,-50,-50,-40,-40,-30],
[-30,-40,-40,-50,-50,-40,-40,-30],
[-30,-40,-40,-50,-50,-40,-40,-30],
[-30,-40,-40,-50,-50,-40,-40,-30],
[-20,-30,-30,-40,-40,-30,-30,-20],
[-10,-20,-20,-20,-20,-20,-20,-10],
[20, 20,  0,  0,  0,  0, 20, 20],
[20, 30, 10,  0,  0, 10, 30, 20]])

kingend=np.array([[-50,-40,-30,-20,-20,-30,-40,-50],
[-30,-20,-10,  0,  0,-10,-20,-30],
[-30,-10, 20, 30, 30, 20,-10,-30],
[-30,-10, 30, 40, 40, 30,-10,-30],
[-30,-10, 30, 40, 40, 30,-10,-30],
[-30,-10, 20, 30, 30, 20,-10,-30],
[-30,-30,  0,  0,  0,  0,-30,-30],
[-50,-30,-30,-30,-30,-30,-30,-50]])


def num_pieces(board):
    s=board.fen().split()[0]
    return sum(c.isalpha() for c in s)


def evaluate(board):
    if(num_pieces(board))<=6:
        wdl=tablebase.probe_wdl(board)
        turn=board.turn
        if((turn==True and wdl==2) or (turn==False and wdl==-2)):
            # Tablebase win
            return 20000
        elif(wdl==2 or wdl==-2):
            # Tablebase loss
            return -20000
        else:
            # Tablebass draw
            return 0
    val = 0
    i=0
    j=0
    blackQueen=False
    whiteQueen=False
    state=board.fen()
    for char in state:
        if char == " ":
            return val
        elif char.isnumeric():
            j+=int(char)
            continue
        elif char == "/":
            i+=1
            j=0
        elif char == 'p':
            val-=pawn[7-i,7-j]
            j+=1
        elif char == 'P':
            val+=pawn[i,j]
            j+=1
        elif char == 'n':
            val-=knight[7-i,7-j]
            j+=1
        elif char == 'N':
            val+=knight[i,j]
            j+=1
        elif char == 'b':
            val-=bishop[7-i,7-j]
            j+=1
        elif char == 'B':
            val+=bishop[i,j]
            j+=1
        elif char == 'r':
            val-=rook[7-i,7-j]
            j+=1
        elif char == 'R':
            val+=rook[i,j]
            j+=1
        elif char == 'q':
            blackQueen=True
            val-=queen[7-i,7-j]
            j+=1
        elif char == 'Q':
            whiteQueen=True
            val+=queen[i,j]
            j+=1
        elif char == 'k':
            blackKing=(i,j)
            j+=1
        elif char == 'K':
            whiteKing=(i,j)
            j+=1
        else:
            print("Unrecognized symbol in FEN input: "+char)
    if(whiteQueen):
        val-=king[7-blackKing[0],7-blackKing[1]]
    else:
        val-=kingend[7-blackKing[0],7-blackKing[1]]
    if(blackQueen):
        val+=king[whiteKing[0],whiteKing[1]]
    else:
        val+=kingend[whiteKing[0],whiteKing[1]]
        
        
def sort_moves(board):
    legal_moves=list(board.legal_moves)
    castle=[]
    checks=[]
    captures=[]
    mates=[]
    indices=list(range(board.legal_moves.count()))
    for i in range(len(legal_moves)):
        legal_moves[i]=board.san(legal_moves[i])
        if '#' in legal_moves[i]:
            mates.append(i)
            indices.remove(i)
        elif '+' in legal_moves[i]:
            checks.append(i)
            indices.remove(i)
        elif 'x' in legal_moves[i]:
            captures.append(i)
            indices.remove(i)
        elif '-' in legal_moves[i]:
            castle.append(i)
            indices.remove(i)
    random.shuffle(indices)
    indices=mates+checks+captures+castle+indices
    return np.take(legal_moves,indices)


def minimax(currdepth, maxdepth, board, alpha, beta):
    if board.outcome() is not None:
        winner=board.outcome().winner
        if winner is None:
            return 0
        elif(winner==True):
            return 20000
        else:
            return -20000
    if currdepth==maxdepth:
        return evaluate(board)
    if board.turn:  # white player
        best = -40000
        moves=sort_moves(board)  
        index_max=-1
        for i in range(len(moves)):
            board.push_san(moves[i])
            val=minimax(currdepth+1, maxdepth, board, alpha, beta)
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
        best=40000
        moves=sort_moves(board)
        index_min=-1
        for i in range(len(moves)):
            board.push_san(moves[i])
            val=minimax(currdepth+1, maxdepth, board, alpha, beta)
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

        
def play():
    color=None
    while color!='w' and color!='b':
        color=input("Welcome to Grant's chess program!\nChoose a color.\nEnter w or b: ")
    board=chess.Board()
    if color == 'b':
        while board.outcome() is None:
            comp_move=minimax(0,3,board,-40000,40000)[1]
            board.push_san(comp_move)
            print(comp_move+"\n")
            print(flip(chess.BaseBoard(board.board_fen()).unicode()))
            print("")
            while True:
                player_move=input("Enter a move: ")
                try:
                    board.push_san(player_move)
                    break
                except:
                    print(player_move+" is not a valid move.\n")
            print(flip(chess.BaseBoard(board.board_fen()).unicode()))
            print("")
    if color == 'w':
        while board.outcome() is None:
            while True:
                player_move=input("Enter a move: ")
                try:
                    board.push_san(player_move)
                    break
                except:
                    print(player_move+" is not a valid move.\n")
            print(chess.BaseBoard(board.board_fen()).unicode())
            print("")
            comp_move=minimax(0,3,board,-40000,40000)[1]
            board.push_san(comp_move)
            print(comp_move+"\n")
            print(chess.BaseBoard(board.board_fen()).unicode())
            print("")
            