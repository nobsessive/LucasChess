# Copyright (c) [2020] [P.H.]
import copy

import numpy as np

import config as game_config
from GameRules import GR
from kerasModel import ModelConfig
from kerasModel import MyModel


class MCTconfig:
    def __init__(self):
        self.inf = 99999
        self.L = 36  # max simulation length
        self.maxPossibleReward = 1
        self.cpuct = game_config.cpuct


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
        # p = os.path.join(os.getcwd(), "lucas_model")
        # self.nn.loadModel(p)
        #
        # print("Model Loaded Successfully")
        # # ==================================================================================
        # def init_layer(layer):
        #     session = K.get_session()
        #     weights_initializer = tf.variables_initializer(layer.weights)
        #     session.run(weights_initializer)
        #
        # layer_under_init = [ l for l in self.nn.model.layers if l.name == "v_head"]
        # for i in range(len(layer_under_init)):
        #     layer_under_init[i].set_weights([np.random.random(layer_under_init[i].get_weights()[0].shape), np.random.random(1)*2-1])

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
        else:
            actionValue, v = self.nn.evaluate(copy.deepcopy(rn.state), rn.turn)
            actionValue = actionValue / np.sqrt(np.sum(actionValue ** 2))
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
            v = self.config.maxPossibleReward
            _, Q = self.nn.evaluate(state, turn)
            for edge in path:
                if edge.turn == turn:
                    edge.W += max(0, Q * v)
                else:
                    edge.W += max(0, (1 - Q) * v)
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
                v = self.config.maxPossibleReward
                if len(path) > 0:
                    for edge in path:
                        if edge.turn != turn:  # opponent wins
                            edge.W += v
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

        # =================display================
        print_pi = np.array(pi)
        localn_list = print_pi[:, 1]
        idx_maxN = np.argwhere(localn_list == max(localn_list))  # could be an array
        if (type(idx_maxN) != type(int)):
            idx_maxN = idx_maxN[0][0]  # the returned array's data is stored at array[i][0]
        selected_edge = self.tree['Edges'][0][int(idx_maxN)]
        print(
            f"mct value for current state (Q): {selected_edge.Q}, P: {selected_edge.P}, N: {selected_edge.N}, W: {selected_edge.W}")
        # =================display================

        return pi


if __name__ == "__main__":
    gr = GR()
    mct = MCTS(5, MCTconfig())
    mct.addRoot(gr.initialBoard, 1)
    print(mct.getPiV())
