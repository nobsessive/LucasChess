# Copyright (c) [2020] [P.H.]
# +++++++++++++++++++++++++++++++++++++++++++++++++++
#  Load model is at MonteCarloTree.py MCTS()
# +++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import pickle
from collections import deque

import NxNoptimal
import config as game_config
from GameRules import GR
from MonteCarloTree import MCTS, MCTconfig
from count import GameSignal, Count


class BrainMemory:
    def __init__(self, max_size, param=None):
        self.HOME_PATH = param
        self.memory_dir = os.path.join(self.HOME_PATH, "memory")
        self.max_size = max_size
        self.usable_memory = deque(maxlen=max_size)
        self.tmp_memory = deque(maxlen=max_size)

    def write2disk(self, mem_number=0):
        name = os.path.join(self.memory_dir, str(mem_number).zfill(8) + '.p', 'wb')
        pickle.dump(self.usable_memory, open(self.memory_dir))

    def addOneFrame(self, state, piv, turn):
        self.tmp_memory.append([state, piv, turn])

    def buildUsableMemory(self, winner, reward):
        while len(self.tmp_memory) > 0:
            t = self.tmp_memory.pop()  # t=[state,[pi,v],turn]
            if t[2] == winner:  # winning move
                t[1][-1] = reward
            else:  # losing move
                t[1][-1] = 0
            self.usable_memory.append(t)
        self.tmp_memory = deque(maxlen=self.max_size)


class Brain:
    def __init__(self, param=None):
        self.HOME_PATH = param
        self.mct = MCTS(game_config.mct_simulate_num, MCTconfig())
        self.gr = GR()
        self.gcnt = Count()
        self.epsilon = game_config.epsilon  # epsilon greedy
        self.mem = BrainMemory(game_config.memory_size, self.HOME_PATH)
        self.game_count = 0
        # self.trained_label = 0

    def getAction(self, cmd):  # cmd.body==(board,turn)
        state = cmd.body[0].copy()
        turn = cmd.body[1]
        winner = cmd.body[2]
        print(f'============================winner :  {winner}')
        trained_label = cmd.trained_label

        # cmd.counter += 1

        # if cmd.counter % 50 == 0:
        #     othercmd = cmd.body[3]
        #     # if othercmd[0] == 1:  # write model
        #     p = os.path.join(self.HOME_PATH, "lucas_model")
        #     self.mct.nn.writeModel(p)
        #     # elif othercmd[0] == 2:  # read model
        #     #     p = os.path.join(self.HOME_PATH, "lucas_model")
        #     #     self.mct.nn.loadModel(p)
        #     # return GameSignal(2, None)
        # if cmd.counter % 5000 == 0:
        #     p = os.path.join(self.HOME_PATH, f"lucas_model_5_thousand_{min(cmd.counter, 5000000)}")
        #     self.mct.nn.writeModel(p)

        if len(winner) > 0:
            self.winnerKnown(winner[0])
            if trained_label == 0:
                # self.mct.nn.train(self.mem.usable_memory)
                pass
            newsig = GameSignal(2, None)
            cmd.trained_label = 1  # do not retrain unless restarted
            return newsig

        # self.gcnt.incrs()
        # self.mct.addRoot(copy.deepcopy(state), turn)
        # pi = self.mct.getPiV()
        # pi = np.array(pi)
        # actn_list = pi[:, 0]
        # localn_list = pi[:, 1]
        # idx_maxN = np.argwhere(localn_list == max(localn_list))  # could be an array
        # if (type(idx_maxN) != type(int)):
        #     idx_maxN = idx_maxN[0][0]  # the returned array's data is stored at array[i][0]
        #
        # piv = []
        # # epsilon greedy
        # self.game_count += 1
        # if np.random.random() < self.epsilon * 2 * (0.5 ** math.log(self.game_count, 100)):
        #     idx_maxN = np.random.randint(0, len(actn_list))
        #     print("-----  This is an epsilon move ----")
        #
        # # store intended move into game signal
        # move_n = actn_list[idx_maxN]
        # move_n = int(move_n + 0.5)

        if turn == -1:
            for ii, row in enumerate(state):
                for jj, nn in enumerate(row):
                    if nn in [-1, 1]:
                        state[ii][jj] *= -1

        state_num = NxNoptimal.state_to_num(state, 0)
        best_move = NxNoptimal.num_to_state(NxNoptimal.par[state_num])[0]
        best_move2d = [best_move[j * game_config.board_rows:j * game_config.board_rows + game_config.board_cols] for j
                       in
                       range(game_config.board_rows)]
        moved_piece, target_place, obstacle = [], [], []

        for i, s in enumerate(best_move2d):
            for j, t in enumerate(s):
                if state[i][j] == 0:
                    if t == 2:
                        obstacle = [i, j]
                    elif t in [-1, 1]:
                        target_place = [i, j]
                elif state[i][j] in [1, -1]:
                    if t == 0 or t == 2:
                        moved_piece = [i, j]
                    if t == 2:
                        obstacle = [i, j]

        move = moved_piece + target_place + obstacle
        self.gcnt.incrs()
        newsig = GameSignal(1, move)

        # use mct simulation to create label for pi_head
        # label for v head will be initialized when winner is known
        # pi = [0] * 577
        # j = 0
        # for i in range(len(actn_list)):
        #     pi[int(actn_list[i])] = localn_list[i]

        # store mct Ni into game signal
        # self.mem.addOneFrame(state, pi, turn)

        return newsig

    def winnerKnown(self, winner):
        self.mem.buildUsableMemory(winner, self.mct.config.maxPossibleReward)

    # def selfLearn(self, cmd):
    #     state = cmd[1][0]
    #     turn = cmd[1][1]
    #     MCTS.addRoot(state, turn)
    #     pi = MCTS.getPiV()
    #     pi = np.array(pi)
    #     ## -- ....
    #     move = self.gr.getMoveWithActn(state, turn, m)
    #     return move

    def observe(self, state):
        pass


if __name__ == "__main__":
    br = Brain()
