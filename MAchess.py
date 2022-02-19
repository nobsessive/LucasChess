# Copyright (c) [2020] [P.H.]


# Ma Chess

import copy
import os
import sys
import tkinter as tk

from PIL import Image, ImageTk

from GameRules import GR
from count import Count


class ChessBoard(tk.Tk):

    # -- internal
    def __init__(self, HumanPlayWhite=True, HumanPlayBlack=True):

        # -- path configure
        if getattr(sys, 'frozen', False):
            self.HOME_PATH = os.path.dirname(sys.executable)
        elif __file__:
            self.HOME_PATH = os.path.dirname(__file__)

        # -- vital assets
        tk.Tk.__init__(self, None)
        self.gr = GR()

        # -- sync with other module
        self.gcnt = Count()
        self.gameMode = 0
        self.engineTurn = 0  # init
        self.othercmd = []
        self.generate_move_flag = 0

        # gui control
        self.freezeboard = 0
        self.clickstate = 0  # 0 wait for click, 1 valid click once, 2 valid click twice

        # -- game parameters

        self.currentstep = 0
        self.bplayer = int(HumanPlayBlack)  # human 1, ai 0
        self.wplayer = int(HumanPlayWhite)
        self.cols = 6
        self.rows = 6
        self.img_backup = {}
        self.pieces = {}
        self.state = [
            [0, 0, 0, -1, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [-1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0]
        ]

        # -- ui
        # super(ChessBoard, self).__init__()
        self.title("Lucas MAchess")

        # ui.0 controllers
        # ui.0.0 menubar
        self.MAmenuBar = tk.Menu(self)
        self.config(menu=self.MAmenuBar)
        filemenu = tk.Menu(self.MAmenuBar)
        settingmenu = tk.Menu(self.MAmenuBar)
        self.MAmenuBar.add_cascade(label="File", menu=filemenu)
        self.MAmenuBar.add_cascade(label='Settings', menu=settingmenu)
        filemenu.add_command(label="open")
        filemenu.add_command(label="save")
        settingmenu.add_command(label='load model', command=self.load_model)
        settingmenu.add_command(label='write model', command=self.write_model)

        # ui.0.1 button
        self.button1 = tk.Label(text='Generate Move')
        self.button1.bind("<ButtonRelease>", self.generate_move)
        self.button1.pack()
        self.button2 = tk.Label(text='restart')
        self.button2.bind("<ButtonRelease>", self.userRestartGame)
        self.button2.pack()
        self.button3 = tk.Label(text='toggle self-play')
        self.button3.bind("<ButtonRelease>", self.toggleSelfTraining)
        self.button3.pack()

        # ui.1 canvas
        canvasBgColor = "#00ff00"
        self.cellSize = 64
        self.whiteCellColor = "#ffd480"
        self.blackCellColor = "#8b4513"
        self.pieceid2name = {
            1: "block",
            2: "king"
        }
        self.loadPieces()
        self.canvasHeight = self.rows * self.cellSize
        self.canvasWidth = self.cols * self.cellSize
        self.canvas = tk.Canvas(width=self.canvasWidth, height=self.canvasHeight,
                                background=canvasBgColor)
        self.canvas.pack()
        self.canvas.bind("<Configure>", self.resizeCanvas)
        self.canvas.bind("<ButtonRelease>", self.mouseclicked)

        # ui.2 label
        self.label1 = tk.Label(self, text='Game Result Pending ...')
        self.label1.pack()

        self.status = 3  # start ; 0 restart, 1 pending, 2 endofgame
        self.turn = self.gr.initialTurn
        self.self_train_flag = False
        self.setBasedOnStatus()

    def userRestartGame(self, event=None):
        self.restart = 1
        self.setBasedOnStatus()

    def generate_move(self, event=None):
        self.generate_move_flag = 1

    def setBasedOnStatus(self):
        if self.status == 0:
            if self.restart == 1:
                self.state = copy.deepcopy(self.gr.initialBoard)
                self.currentstep = 0

                self.turn = self.gr.initialTurn
                self.gameResult = self.gr.initialGameResult
                self.trace = {0: [self.state, None]}
                self.restart = 0

                print("New Game: step %d, turn: %d, result: %d, last move: %s status: %d"
                      % (self.currentstep, self.turn, self.gameResult, [-1], self.status))
            elif self.turn != self.gr.initialTurn:
                self.status = 1
                self.setBasedOnStatus()
        elif self.status == 1:
            if self.restart == 1:
                self.status = 0
                self.setBasedOnStatus()
            else:
                if self.gr.judge(self.state, self.turn) != 0:
                    self.gameResult = -self.turn
                    self.status = 2
                    self.setBasedOnStatus()
        elif self.status == 2:
            # sleep(100)
            if self.restart == 1:
                self.status = 0
                self.setBasedOnStatus()
        elif self.status == 3:
            self.restart = 0
            self.gameResult = self.gr.initialGameResult
            if self.turn != self.gr.initialTurn:
                self.status = 1
                self.setBasedOnStatus()
        self.update()

    def loadPieces(self):
        # img=Image.open("images\\aaa.png",Image.ANTIALIAS)
        root_dir = os.path.join(self.HOME_PATH, 'images', 'MAchess')
        name = 'king'
        # print(fullname)
        # img=Image.open(fullname)
        # img=ImageTk.PhotoImage(file=fullname)
        # img=tk.PhotoImage(img)
        wname = os.path.join(root_dir, "whitepieces", name + '.png')
        bname = os.path.join(root_dir, "blackpieces", name + '.png')
        # bname=root_dir+"blackpieces\\"+name+'.png'
        imgw = Image.open(wname)
        imgw = ImageTk.PhotoImage(imgw)
        self.img_backup.update({1: imgw})
        imgb = Image.open(bname)
        imgb = ImageTk.PhotoImage(imgb)
        self.img_backup.update({-1: imgb})
        blkname = os.path.join(root_dir, "block.png")
        imgblk = Image.open(blkname)
        imgblk = ImageTk.PhotoImage(imgblk)
        self.img_backup.update({2: imgblk})
        # self.pieceColorInvert()
        # self.pieces.update({"nothing":img})

    def placepiece(self, row, column, id=None, natural_name="nothing"):
        x = (column * self.cellSize)
        y = (row * self.cellSize)
        self.canvas.create_image(x, y, image=self.img_backup[id], tags="pieces", anchor='nw')

    def move(self):
        if self.freezeboard != 0:
            return
        if self.judgeclick() == False:
            return
        r1, c1 = self.select1
        r2, c2 = self.select2
        r3, c3 = self.select3
        t = self.state[r1][c1]
        self.state[r1][c1] = 0
        self.state[r2][c2] = t
        self.state[r3][c3] = 2

        self.generate_move_flag = 0
        self.turn = -self.turn
        self.currentstep += 1

        self.setBasedOnStatus()
        # print("New State: step %d, turn: %d, result: %d, last move: %s status: %d" %
        #       (self.currentstep, self.turn, self.gameResult, [r1, c1, r2, c2, r3, c3], self.status))
        self.update()

    def update(self):
        # board
        minwh = min(self.canvasHeight, self.canvasWidth)
        self.canvas.delete("pieces")
        self.cellSize = int(minwh / self.rows)
        color_list = [self.whiteCellColor, self.blackCellColor]
        for i in range(self.rows):
            x1 = i * self.cellSize
            x2 = x1 + self.cellSize - 1
            for j in range(self.cols):
                currentColorIndex = (i + j) % 2
                y1 = j * self.cellSize
                y2 = y1 + self.cellSize
                self.canvas.create_rectangle(x1, y1, x2, y2, outline='black', fill=color_list[currentColorIndex],
                                             tag='cells')
        for i in range(self.rows):
            for j in range(self.cols):
                s = self.state[i][j]
                if s != 0:
                    self.placepiece(i, j, s)
        self.canvas.tag_raise("pieces")
        self.canvas.tag_lower("cells")

        # game result
        self.victoryWindow()

    def victoryWindow(self):
        c = self.status
        if c != 2:
            self.label1['text'] = 'Game Result Pending ...'
            return
        c = self.gameResult
        if c == 1:
            self.label1['text'] = 'White Win!'
        else:
            self.label1['text'] = 'Black Win!'
        print("End of one Iteration")

    def setState(self, state):
        if self.freezeboard == 1:
            return
        self.state = state
        self.update()

    def on_closing(self):
        pass

    # -- human interaction
    def write_model(self, event=None):
        self.othercmd = [1]

    def load_model(self, event=None):
        self.othercmd = [2]

    def resizeCanvas(self, event):
        # -- resize and re-draw
        self.canvasWidth = event.width
        self.canvasHeight = event.height
        self.update()

    def mouseclicked(self, event):
        row = event.y // self.cellSize
        col = event.x // self.cellSize
        self.lastrow = row
        self.lastcol = col
        self.respondClick()

    def respondClick(self):
        row = self.lastrow
        col = self.lastcol
        if self.state[row][col] != 0:
            if self.clickstate == 0:
                self.clickstate = 1
                self.select1 = [row, col]
                return
            elif self.clickstate == 1:

                self.clickstate = 0
                return
            else:
                self.clickstate = 0
                if row == self.select1[0] and col == self.select1[1]:
                    self.select3 = self.select1
                    self.move()
                return
        else:
            if self.clickstate == 1:
                self.clickstate = 2
                self.select2 = [row, col]
                return
            elif self.clickstate == 2:
                self.clickstate = 0
                self.select3 = [row, col]
                self.move()

    def judgeclick(self):

        r1 = self.select1[0]
        c1 = self.select1[1]
        if self.state[r1][c1] != self.turn:
            return False
        # move1 to move2
        r2 = self.select2[0]
        c2 = self.select2[1]
        dr = r2 - r1
        dc = c2 - c1
        if dr == 0:
            dir = (c2 - c1) // abs(c2 - c1)
            i = c1 + dir
            while i != c2:
                if self.state[r1][i] != 0:
                    return False
                i += dir
            if self.state[r2][c2] != 0:
                return False
        elif dc == 0:
            dir = (r2 - r1) // abs(r2 - r1)
            i = r1 + dir
            while i != r2:
                if self.state[i][c1] != 0:
                    return False
                i += dir
            if self.state[r2][c2] != 0:
                return False
        else:
            if abs(dr) != abs(dc):
                return False
            dir1 = (r2 - r1) // abs(r2 - r1)
            dir2 = (c2 - c1) // abs(c2 - c1)
            j = c1 + dir2
            for i in range(r1 + dir1, r2 + dir1, dir1):
                if self.state[i][j] != 0:
                    return False
                j += dir2
        # move2 to move3
        dr = self.select3[0] - self.select2[0]
        dc = self.select3[1] - self.select2[1]
        if abs(dr) > 1 or abs(dc) > 1:
            return False

        return True

    def toggleSelfTraining(self, event=None):
        self.self_train_flag = not self.self_train_flag

    # -- engine part
    def engineApplyMove(self, body):
        print('engine move %d : %s' % (self.currentstep, body))
        # set-up
        b = body
        self.select1 = [b[0], b[1]]
        self.select2 = [b[2], b[3]]
        self.select3 = [b[4], b[5]]
        self.move()

    def getBattleInfo(self):
        winner = []
        if self.self_train_flag == True:
            self.generate_move_flag = 1

        if self.generate_move_flag == 1:
            cmd = -1
        elif self.gameMode == 0:
            cmd = 0  # do nothing
        elif self.gameMode == 1:  # human vs engine
            if self.turn == self.engineTurn:
                cmd = -1  # need action

        else:
            cmd = 0

        if self.gameResult in self.gr.nonePendingResults:
            winner.append(copy.deepcopy(self.gameResult))
            if self.generate_move_flag == 1:
                self.generate_move_flag = 0
                self.userRestartGame()
            cmd = -1
        state = copy.deepcopy(self.state)

        u = []
        if len(self.othercmd) > 0:
            u = copy.deepcopy(self.othercmd)
            self.othercmd = []
            cmd = -1

        return [cmd, state, self.turn, winner, u]

    def freeze(self):
        self.freezeboard = True

    def defreeze(self):
        self.freezeboard = False

    # -- util function
    def getMove(self, event):
        r1, c1 = self.select1
        r2, c2 = self.select2
        r3, c3 = self.select3
        return [r1, c1, r2, c2]


class State:
    def __init__(self, n=None):
        if n == 0:  # initial state
            self.s = [
                [0, 0, 0, -1, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [-1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0]
            ]
            self.turn = 1


class Game:
    def __init__(self):
        self.current_step = 0
        self.current_state = State(0)
        self.state_path = [self.current_state]

    def act(self, action):
        pass


if __name__ == "__main__":
    cb = ChessBoard()
    cb.protocol("WM_DELETE_WINDOW", cb.on_closing)
    cb.mainloop()
