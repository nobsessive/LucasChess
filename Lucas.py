# Copyright (c) [2020] [P.H.]
# +++++++++++++++++++++++++++++++++++++++++++++++++++
#  Load model is at MonteCarloTree.py MCTS()
# +++++++++++++++++++++++++++++++++++++++++++++++++++

import copy
import threading

from Brain import Brain
from MAchess import ChessBoard
from count import Count, GameSignal

globalsig = GameSignal(0, None)


class Lucas:

    def __init__(self):
        self.gcnt = Count()
        self.status = 1  # 1 init, -1 thinking, 0 need action
        self.turn = 1  # white move
        global globalsig
        self.oldsig = globalsig
        self.ui = ChessBoard()
        self.HOME_PATH = copy.deepcopy(self.ui.HOME_PATH)
        self.brain = Brain(copy.deepcopy(self.HOME_PATH))
        self.checkStatus()

        self.ui.mainloop()

    def checkStatus(self):
        global globalsig
        cmd, board, turn, winner, othercmd = self.ui.getBattleInfo()
        if self.status == -1:  # thinking
            if globalsig.status == 1:  # receive new move
                globalsig.status = 0
                self.ui.defreeze()
                self.ui.engineApplyMove(globalsig.body)
                self.status = 0  # idle
            elif globalsig.status == 2:  # train completed
                globalsig.status = 0
                self.ui.defreeze()
                self.status = 0  # idle
        elif cmd == -1:
            self.ui.freeze()
            self.oldsig = GameSignal(-1, (board, turn, winner, othercmd))
            globalsig.copy(self.oldsig)
            self.thrd = threading.Thread(target=self._getAction, args=())
            self.thrd.start()
            self.status = -1  # thinking

        self.ui.after(100, lambda: self.checkStatus())

    def _getAction(self):
        global globalsig
        # if self.ui.restart == 1 or self.ui.gameResult in self.ui.gr.nonePendingResults:
        if self.ui.currentstep == 0:
            globalsig.trained_label = 0
        # if globalsig.counter%10==0 and globalsig!=0:
        #     globalsig.body[3]=[0]
        # print("status====")
        # print(self.status)
        globalsig.counter += 1
        newsig = self.brain.getAction(globalsig)
        globalsig.copy(newsig)

    def update(self, signal):
        self.ui.act(cmd=signal)

    def getCommand(self):
        return self.ui.getMove()

    def getNewEvents(self):
        self.ui.getNewEvents()


if __name__ == "__main__":
    L = Lucas()
