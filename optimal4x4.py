import copy

import config
from GameRules import GR


class Alpha_Beta_Search:
    def search4x4(self, state=None, turn=1, my_turn=1):
        root_state = copy.deepcopy(config.init_chess_state) if state == None else state
        self.gr = GR()
        return self.play_alpha_beta(root_state, current_turn=turn, my_turn=1, depth=0)

    def play_alpha_beta(self, state, current_turn=1, my_turn=1, depth=0):

        # ===================display===========================
        self.searched_node_cnt = 0
        self.searched_depth1_node_cnt = 0
        self.arr_searchd_node_cnt = [0] * 12
        # ===================display===========================
        self.result = self.gr.judge(state, current_turn)

        if self.result != 0:
            if current_turn == 1:
                print('The winner is black!')
            elif self.result == '.':
                print('The winner is white!')
            return

        if current_turn == -1:
            v, state_array, search_depth = self.min_alpha_beta(state, -1, depth, -2, 2)

        else:
            v, state_array, search_depth = self.max_alpha_beta(state, 1, depth, -2, 2)  # 2 is inf+1, -2 is inf-1
        return v, [state] + state_array, search_depth

    def max_alpha_beta(self, state, turn, depth, alpha, beta):
        state_array = []
        search_depth = depth  # search depth is depth if state is leaf, else {depth+1 if one child is max leaf node, else { results from min_alpha_beta}}
        maxv = -2

        result = self.gr.judge(state, turn)

        if result != 0:
            return (-1, [], depth)

        legal_move_list = self.gr.getAllowedMoves(copy.deepcopy(state), turn, 'actn')
        selected_child = None
        for actn in legal_move_list:
            child_state = self.gr.takeAction(state, actn, turn)  # deepcopy is included
            if self.gr.judge(child_state, -turn) != 0:  # result acquired, turn wins this alpha_beta_node
                m = 1
                tmp_search_depth = depth + 1
                tmp_state_array = []
                selected_child = child_state
            else:
                m, tmp_state_array, tmp_search_depth = self.min_alpha_beta(child_state, -turn, depth + 1, alpha, beta)
            if m >= maxv:
                if m > maxv or (m < 0 and tmp_search_depth > search_depth) or (
                        m > 0 and tmp_search_depth < search_depth):
                    maxv = m
                    state_array = tmp_state_array
                    search_depth = tmp_search_depth
                    selected_child = child_state

        # ===================display===========================
        self.searched_node_cnt += 1
        self.arr_searchd_node_cnt[depth] += 1
        if self.searched_node_cnt % 1000 == 0:
            print(f"searched node: {self.searched_node_cnt}, node array: {self.arr_searchd_node_cnt}")
        # ===================display===========================

        return (maxv, [selected_child] + state_array, search_depth)

    def min_alpha_beta(self, state, turn, depth, alpha, beta):

        state_array = []
        search_depth = depth  # search depth is depth if state is leaf, else {depth+1 if one child is max leaf node, else { results from min_alpha_beta}}
        minv = 2

        result = self.gr.judge(state, turn)

        if result != 0:
            return (-1, [], depth)

        legal_move_list = self.gr.getAllowedMoves(copy.deepcopy(state), turn, 'actn')
        selected_child = None
        for actn in legal_move_list:
            child_state = self.gr.takeAction(state, actn, turn)  # deepcopy is included
            if self.gr.judge(child_state, -turn) != 0:  # result acquired, turn win this alpha_beta_node
                m = -1
                tmp_search_depth = depth + 1
                tmp_state_array = []
                selected_child = child_state
            else:
                m, tmp_state_array, tmp_search_depth = self.max_alpha_beta(child_state, -turn, depth + 1, alpha, beta)
            if m <= minv:
                if m < minv or (m > 0 and tmp_search_depth > search_depth) or (
                        m < 0 and tmp_search_depth < search_depth):
                    minv = m
                    state_array = tmp_state_array
                    search_depth = tmp_search_depth
                    selected_child = child_state

        # ===================display===========================
        self.searched_node_cnt += 1
        self.arr_searchd_node_cnt[depth] += 1
        if self.searched_node_cnt % 1000 == 0:
            print(f"searched node: {self.searched_node_cnt}, node array: {self.arr_searchd_node_cnt}")
        # ===================display===========================

        return (minv, [selected_child] + state_array, search_depth)


if __name__ == "__main__":
    abs = Alpha_Beta_Search()
    v, state_array, search_depth = abs.search4x4()
    f = open("4x4optimal.txt", "w+")
    print(f"v: {v}, search_depth: {search_depth}\n\n")
    f.write(f"v: {v}, search_depth: {search_depth}\n\n")

    for x in state_array:
        for y in x:
            print(y)
            f.write(str(y) + '\n')
        f.write('---------------\n')
        print('---------------')
    f.close()

    # =========================================

    # v, state_array, search_depth = abs.search4x4(config.question_state)
    # f = open("question_4x4optimal.txt", "w+")
    # print(f"v: {v}, search_depth: {search_depth}\n\n")
    # f.write(f"v: {v}, search_depth: {search_depth}\n\n")
    #
    #
    # for x in state_array:
    #     for y in x:
    #         print(y)
    #         f.write(str(y)+'\n')
    #     f.write('---------------\n')
    #     print('---------------')
    # f.close()
