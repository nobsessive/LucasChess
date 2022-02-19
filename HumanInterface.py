# Copyright (c) [2020] [P.H.]


import threading
import time

from MAchess import ChessBoard

# from Brain import Brain

testcmd = 0


class HI:

    def __init__(self):
        global testcmd
        self.itg = 0
        self.oldcmd = testcmd
        self.currentitg = self.itg
        self.ui = ChessBoard()
        self.status = 0  # 0 need action, -1 thinking
        self.test(0)

        self.ui.mainloop()

    def test(self, n):
        print('test%f' % n)
        if self.status == 0:
            thrd = threading.Thread(target=self.test_getAction, args=(self.oldcmd,))
            self.status = -1
            thrd.start()
        elif self.status == -1:

            if self.oldcmd != testcmd:
                print('new cmd received %d' % testcmd)
                self.oldcmd = testcmd
                self.status = 0
            else:
                print('thinking oldcmd %d testcmd %d' % (self.oldcmd, testcmd))
        else:
            print('param %s' % (self.itg, testcmd))
            self.itg = testcmd

        self.ui.after(100, lambda: self.test(self.itg))

    def test_getAction(self, n):
        global testcmd
        print('here')
        time.sleep(1)
        testcmd = n + 1

    def update(self, signal):
        self.ui.act(cmd=signal)

    def getCommand(self):
        return self.ui.getMove()

    def getNewEvents(self):
        ui.getNewEvents()


if __name__ == "__main__":
    hi = HI()
