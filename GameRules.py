# Copyright (c) [2020] [P.H.]


# from MAchess import Game
import copy

import config


class Move:
    def __init__(self, r1, c1, r2, c2, p):
        self.r1 = r1
        self.c1 = c1
        self.r2 = r2
        self.c2 = c2
        self.p = p  # 0 to 7     0 1 2, 3 _ 4, 5 6 7


class GR:
    def __init__(self):
        # self.game=Game()
        self.cols = config.board_cols
        self.rows = config.board_rows

        self.initialBoard = copy.deepcopy(config.init_chess_state)
        self.initialGameResult = 0
        self.nonePendingResults = [1, -1]
        self.initialTurn = 1
        self.pick_piece_thrs = self.cols * self.rows * 8  # threshold for picking up a queen

    # export functions
    def getAllowedMoves(self, board, turn, mode='coord'):
        x, y = self.findPiece(board, turn)
        a = x
        b = y
        # put two pieces in order
        if x[0] > y[0]:
            a = y
            b = x
        elif x[0] == y[0]:
            if x[1] > y[1]:
                a = y
                b = x

        s = []
        if mode == 'coord':
            s += self.gmove(a, board, mode)
            s += self.gmove(b, board, mode)
        else:  # actn
            s += self.gmove(a, board, mode)
            t = []
            t += self.gmove(b, board, mode)
            for i in t:
                s.append(i + self.pick_piece_thrs)
        return s

    def judge(self, board, turn):
        s = self.getAllowedMoves(board, turn)

        if len(s) == 0:
            return -1
        else:
            return 0

    def takeAction(self, b, actn, turn):
        board = copy.deepcopy(b)
        a = self.actn2move(actn, board, turn)
        board[a[0]][a[1]] = 0
        board[a[2]][a[3]] = turn
        board[a[4]][a[5]] = 2
        return board

    # determine move coordinate by action number
    #
    def actn2move(self, actn, board, turn):
        x, y = self.findPiece(board, turn)
        a = x
        b = y
        # put two pieces in order
        if x[0] > y[0]:
            a = y
            b = x
        elif x[0] == y[0]:
            if x[1] > y[1]:
                a = y
                b = x

        if actn >= self.pick_piece_thrs:
            u = b
            actn -= self.pick_piece_thrs
        else:
            u = a
        r1 = u[0]
        c1 = u[1]
        k = actn // 8
        r2 = k // self.rows
        c2 = k % self.rows
        j = actn % 8
        ll = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
        r3 = ll[j][0] + r2
        c3 = ll[j][1] + c2

        return [r1, c1, r2, c2, r3, c3]

    # util functions
    def erow(self, coord, board):
        r, c = coord
        p = []
        for i in range(c + 1, self.cols):
            if board[r][i] != 0:
                break
            else:
                p.append([r, i])
        i = c - 1
        while i >= 0:
            if board[r][i] != 0:
                break
            else:
                p.append([r, i])
            i -= 1
        return p

    def ecol(self, coord, board):
        r, c = coord
        p = []
        for i in range(r + 1, self.rows):
            if board[i][c] != 0:
                break
            else:
                p.append([i, c])
        i = r - 1
        while i >= 0:
            if board[i][c] != 0:
                break
            else:
                p.append([i, c])
            i -= 1
        return p

    def edig(self, coord, board):
        r, c = coord
        p = []

        # main diag
        step = min(self.rows - r - 1, self.cols - c - 1)
        for i in range(1, step + 1):
            if board[r + i][c + i] != 0:
                break
            else:
                p.append([r + i, c + i])
        step = min(r, c)
        for i in range(1, step + 1):
            if board[r - i][c - i] != 0:
                break
            else:
                p.append([r - i, c - i])
        # another diag
        step = min(self.rows - r - 1, c)
        for i in range(1, step + 1):
            if board[r + i][c - i] != 0:
                break
            else:
                p.append([r + i, c - i])
        step = min(r, self.cols - c - 1)
        for i in range(1, step + 1):
            if board[r - i][c + i] != 0:
                break
            else:
                p.append([r - i, c + i])
        return p

    # generate every possible shift of a piece
    # designed to follow by gm2 which places every possible obstacle around a piece
    def gm1(self, coord, board):
        p = []
        p += self.erow(coord, board)
        p += self.ecol(coord, board)
        p += self.edig(coord, board)
        return p

    # denoted on comment gm1
    def gm2(self, coord, board, mode='coord'):
        d = []
        r, c = coord
        if coord[0] == 0:
            dx = [0, 1]
        elif coord[0] == self.rows - 1:
            dx = [-1, 0]
        else:
            dx = [0, -1, 1]

        if coord[1] == 0:
            dy = [0, 1]
        elif coord[1] == self.cols - 1:
            dy = [0, -1]
        else:
            dy = [0, -1, 1]
        if mode == 'coord':
            for i in dx:
                for j in dy:
                    if i == j and i == 0:
                        continue
                    if board[r + i][c + j] == 0:
                        d.append([r + i, r + j])
        else:  # actn
            k = [[0, 1, 2], [3, 1000, 4], [5, 6, 7]]
            for i in dx:
                ii = i + 1
                for j in dy:
                    if i == j and i == 0:
                        continue
                    jj = j + 1
                    if board[r + i][c + j] == 0:
                        d.append(k[ii][jj])
        return d

    # the following function
    # generates every legal move for a specific board with regard to mode
    # actn mode: return a list of action numbers
    # cood mode: return a list of coordinates
    def gmove(self, coord, board, mode):
        s = []
        x, y = coord
        # get legal move for piece
        bop = copy.deepcopy(board)
        bop[x][y] = 0
        mv1 = self.gm1(coord, board)
        if mode == 'actn':
            r = self.rows
            c = self.cols
            for i in mv1:
                base = i[0] * r + i[1]
                mv2 = self.gm2(i, bop, 'actn')
                for j in mv2:
                    s.append(base * 8 + j)
        else:  # m1m2 :
            for i in mv1:
                tmp = self.gm2(i, bop)
                c = []
                for j in range(len(tmp)):
                    c.append([tmp[j][0] + i[0], tmp[j][1] + i[1]])
                tmp = [i + j for j in c]
                s += tmp
        return s

    def findPiece(self, board, piece):
        p = []
        for r in range(self.rows):
            for c in range(self.cols):
                if board[r][c] == piece:
                    p.append([r, c])
        return p


if __name__ == "__main__":
    gr = GR()
