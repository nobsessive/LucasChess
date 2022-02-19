# Copyright (c) [2020] [P.H.]
import copy
import os

import numpy as np

from GameRules import GR
from kerasModel import ModelConfig
from kerasModel import MyModel


class MCTconfig:
    def __init__(self):
        self.inf = 99999
        self.L = 36  # max simulation length
        self.maxPossibleReward = 1
        self.cpuct = 0.1


class Node:
    def __init__(self, state, turn, parentIndex):  # a state defined by GR
        self.state = state
        self.turn = turn
        self.parentIndex = parentIndex


class Edge:
    def __init__(self, parentIndex, actn):
        self.N = 0
        self.W = 0
        self.Q = 0
        self.P = 0
        self.actn = actn
        self.childIndex = None
        self.parentIndex = parentIndex


# turn is -1 or 1
class MCTS():
    def __init__(self, sim_num, config):
        self.gr = GR()
        self.sim_num = sim_num
        self.config = config
        self.nn = MyModel(ModelConfig())
        # =================================================================================
        #  Load Model Here
        p = os.path.join(os.getcwd(), "lucas_model")
        self.nn.loadModel(p)

        print("Model Loaded Successfully")
        # ==================================================================================

    def addRoot(self, state, turn):
        self.tree = {'Nodes': [],
                     'Edges': []
                     }
        self.expandLeafNode(state, turn, None)
        self.simulate()
        return

    def expandLeafNode(self, state, turn, parentIndex, path=[]):
        st = copy.deepcopy(state)
        rn = Node(st, turn, parentIndex)

        self.tree['Nodes'].append(rn)

        a = self.gr.getAllowedMoves(copy.deepcopy(rn.state), turn, 'actn')
        if len(a) == 0:
            self.tree['Edges'].append([])
            v = -self.config.maxPossibleReward
        else:

            actionValue, v = self.nn.evaluate(copy.deepcopy(rn.state), rn.turn)
            p = []
            for actn in a:
                e = Edge(parentIndex=0, actn=actn)
                e.N = 0
                e.W = 0
                e.Q = 0
                e.P = actionValue[actn]
                e.parentIndex = parentIndex
                e.turn = turn
                p.append(e)
            self.tree['Edges'].append(p)

        # backfill
        if len(path) > 0:
            leafplayer = turn
            for edge in path:
                if edge.turn == turn:
                    edge.W += v
                else:
                    edge.W += -v
                edge.N += 1
                edge.Q = edge.W / edge.N

    def simulate(self):
        for sn in range(self.sim_num):
            cix = 0  # current node's index
            path = []

            # -- determine a leaf node
            t = 0
            while len(self.tree['Edges'][cix]) != 0 and t < self.config.L:
                t += 1
                edges = self.tree['Edges'][cix]
                maxqu = -self.config.inf
                sum_N = 0
                for g in edges:
                    sum_N += g.N
                choosen = 0
                for i, g in enumerate(edges):
                    u = self.config.cpuct * g.P * np.sqrt(sum_N) / (1 + g.N)
                    q = g.Q
                    squ = q + u
                    if squ > maxqu:
                        choosen = g.actn
                        choosenEdge = g
                        maxqu = squ

                path.append(choosenEdge)

                if choosenEdge.N == 0:  # leaf node
                    break
                else:
                    cix = choosenEdge.childIndex
                    # no need to increase N for choosenEdge, backfill() will do

            # -- add new State to tree
            if len(self.tree['Edges'][cix]) == 0:  # end game
                turn = self.tree['Nodes'][cix].turn
                v = -self.config.maxPossibleReward
                if len(path) > 0:
                    for edge in path:
                        if edge.turn == turn:
                            edge.W += v
                        else:
                            edge.W += -v
                        edge.N += 1
                        edge.Q = edge.W / edge.N
            else:  # unexpanded node
                turn = self.tree['Nodes'][cix].turn
                newst = self.gr.takeAction(self.tree['Nodes'][cix].state, choosen, turn)
                choosenEdge.childIndex = len(self.tree['Nodes'])
                self.expandLeafNode(newst, -turn, cix, path)
        return

    # return information(train_pi:Ni/Sum(Ni), q{action_value}:Wi/Ni) for each edge of root node
    def getPiV(self):
        if len(self.tree['Nodes']) == 0:
            return
        pi = []
        sumn = 0
        for i, e in enumerate(self.tree['Edges'][0]):
            sumn += e.N
        for e in self.tree['Edges'][0]:
            pi.append([e.actn, 1.0 * e.N / sumn])
        return pi


if __name__ == "__main__":
    gr = GR()
    mct = MCTS(5, MCTconfig())
    mct.addRoot(gr.initialBoard, 1)
    print(mct.getPiV())
