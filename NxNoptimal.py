"""
turn: 0: white, 1: black
piece: -1: black, 0: space, 1: white, 2: obstacle
"""
import copy
import math

import config
from GameRules import GR


def comb(n, k):
    a = 1
    for i in range(n - k + 1, n + 1):
        a *= i
    return a // math.factorial(k)


r, c = config.board_rows, config.board_cols

side_combinations = comb(4, 2)
position_combinations = comb(r * c, 4)
obstacles_combinations = 2 ** (r * c - 4)

total_state_num = side_combinations * position_combinations * obstacles_combinations * 2
piece_position_table = []
side_position_table = []
inv_piece_position_table = {}
inv_side_position_table = {}

gr = GR()  # game rule


def make_position_table(t, comb_num, limit):
    k = list(range(t))
    position_table = []
    inv_position_table = {}
    for i in range(comb_num):
        position_table.append(k.copy())
        inv_position_table.update({frozenset(k.copy()): i})
        for j in range(t - 1, -1, -1):
            if k[j] < limit - (t - j):
                k[j] += 1
                for h in range(j + 1, t):
                    k[h] = k[h - 1] + 1
                break
            else:
                if j > 0 and k[j - 1] + 1 < k[j] - (t - j):
                    k[j - 1] = k[j - 1] + 1
                    for h in range(j, t):
                        k[h] = k[h - 1] + 1
                    break
    # print(position_table, len(position_table))
    return position_table, inv_position_table


# return 1d state with respect to state number
def num_to_state(n):
    state = [0] * r * c

    turn = n % 2
    n //= 2
    position_num = n % position_combinations
    n //= position_combinations
    side_num = n % side_combinations
    n //= side_combinations
    obstacles_num = n

    positions = piece_position_table[position_num]
    whites = side_position_table[side_num]
    blacks = [i for i in range(4) if i not in whites]

    state[positions[whites[0]]] = state[positions[whites[1]]] = 1
    state[positions[blacks[0]]] = state[positions[blacks[1]]] = -1

    for i in range(r * c):
        if state[i] in [-1, 1]:
            continue
        is_obstacle = obstacles_num % 2
        if is_obstacle == 1:
            state[i] = 2
        obstacles_num //= 2

    return state, turn


def state_to_num(state, turn, state_dim=2):
    if state_dim == 2:
        state = [i for j in state for i in j]  # flatten

    num = turn

    position = []
    for i in range(r * c):
        if state[i] in [-1, 1]:
            position.append(i)
    position_num = inv_piece_position_table[frozenset(position)]
    num += position_num * 2

    side = []
    tmp = 0
    for i in range(r * c):
        if state[i] == 1:  # from the perspective of white
            side.append(tmp)
        if state[i] in [-1, 1]:
            tmp += 1
    side_num = inv_side_position_table[frozenset(side)]
    num += side_num * 2 * position_combinations

    obstacle_num = 0
    tmp = 1
    for i in range(r * c):
        if state[i] == 2:
            obstacle_num += tmp
        if state[i] not in [-1, 1]:
            tmp *= 2
    num += obstacle_num * 2 * position_combinations * side_combinations

    return num


# get allowed move for a given state, return a list of states
def get_moved_states(state, turn):
    state2d = [state[j * r:j * r + c] for j in range(r)]

    def gen_moves(state2duc, x, y):
        state2d = state2duc.copy()
        destination = []  # coordinates of destination where we can put the piece back
        dx = [-1, -1, 0, 1, 1, 1, 0, -1]  # north, northeast, east, ... , northwest
        dy = [0, 1, 1, 1, 0, -1, -1, -1]
        # iterate through row, column, and diagonals
        piece_color = state2d[x][y]
        state2d[x][y] = 0
        # x,y start coordinates; p, q dst coordinates; r, s block coordinates
        xlim, ylim = len(state2d), len(state2d[0])

        def judge_oor_or_ne(x, y):  # (out of range or non-empty) judge
            if x > (xlim - 1) or x < 0 or y > (ylim - 1) or y < 0 or state2d[x][y] != 0:
                return 1
            return 0

        def look_around(x, y):  # look around to see which squares can we put blocks
            ret = []
            for i in range(len(dx)):
                if judge_oor_or_ne(x + dx, y + dy) == 0:
                    ret.append([x + dx, y + dy])
            return ret

        for i in range(len(dx)):
            cx, cy = x, y
            while judge_oor_or_ne(cx + dx[i], cy + dy[i]) == 0:
                cx, cy = cx + dx[i], cy + dy[i]
                if state2d[cx][cy] == 0:
                    block_able_list = look_around(cx, cy)
                    if block_able_list:
                        for bal in block_able_list:
                            st = state2d.copy()
                            st[cx][cy] = piece_color
                            st[bal[0]][bal[1]] = 2
                            destination.append(st)
                else:
                    break
        return destination

    state_list = []
    m, n = len(state2d), len(state2d[0])
    for i in range(m):
        for j in range(n):
            if state2d[i][j] == turn:
                state_list += gen_moves(state2d.copy(), i, j)
    return state_list


# return a list of state2d consisting reversed states of state
def reverse_move(state, turn):
    def remove_target_piece_and_obstacle(state2d, i, j):
        ret = []
        dx = dy = [-1, 0, 1]
        for p in dx:
            for q in dy:
                x, y = p + i, q + j
                if x < 0 or x >= r or y < 0 or y >= c:
                    continue
                if state2d[x][y] == 2:
                    cpst = copy.deepcopy(state2d)
                    cpst[x][y], cpst[i][j] = 0, 0
                    ret.append(cpst)
        return ret

    def move_piece_back(state2d_list, i, j, target_side):
        destination = []  # coordinates of destination where we can put the piece back
        dx = [-1, -1, 0, 1, 1, 1, 0, -1]  # north, northeast, east, ... , northwest
        dy = [0, 1, 1, 1, 0, -1, -1, -1]
        # iterate through row, column, and diagonals
        for state2d in state2d_list:
            for k in range(len(dx)):
                x, y = i, j
                while True:
                    x += dx[k]
                    y += dy[k]
                    if x < 0 or x >= r or y < 0 or y >= c:
                        break
                    if state2d[x][y] == 0:
                        cpst = copy.deepcopy(state2d)
                        cpst[x][y] = target_side
                        destination.append(cpst)
                    else:
                        break
        return destination

    # ---------------------- sub-functions end -----------------------
    target_side = -1 if turn == 0 else 1
    state2d = [state[j * r:j * r + c] for j in range(r)]
    out = []
    for i in range(r):
        for j in range(c):
            if state2d[i][j] == target_side:
                tmp_out = remove_target_piece_and_obstacle(state2d, i, j)
                out += move_piece_back(tmp_out, i, j, target_side)
    return out


def unit_test():
    # ------------------------------- test reverse_move ----------------------------------------
    state, turn = num_to_state(3000)
    print(f"state : {state}, turn: {turn}\n******************")
    ret = reverse_move(state, turn)
    for i in ret:
        for j in range(r):
            print(i[j])
        print("-------------------")

    # ------------------------------- test state_to_num ----------------------------------------
    test_state = [
        [2, -1, 0],
        [-1, 2, 2],
        [0, 1, 1]
    ]
    stn = state_to_num(test_state, 0)
    print(stn)
    print(num_to_state(stn))


def optimal_strategy():
    # distance to win, 0 is leaf node
    dtw = [-1] * total_state_num
    # store the number of parent node, leaf nodes have no parents since the tree grows to the bottom
    # -2 means un-initialized, -1 means leaf node
    par = [-2] * total_state_num

    node_cnt = 1
    for i in range(1, total_state_num, 2):  # find all black's lose state
        # ======================================= display =======================================
        if node_cnt % 10000 == 0:
            print(
                f"********** overall expanded node number: {node_cnt} (state number: {total_state_num}) **************")
        node_cnt += 1
        # ======================================= display =======================================
        s, t = num_to_state(i)
        s = [s[j * r:j * r + c] for j in range(r)]
        if gr.judge(s, t) != 0:
            dtw[i] = 0
            par[i] = -1

    parent_turn = 1
    for current_distance in range(1, r * c + 1):
        print(f"========================current distance {current_distance}===========================")
        current_turn = (parent_turn + 1) % 2
        for i in range(total_state_num):
            if i % 10000 == 0:
                print(f"---- inspected: {i}/{total_state_num} ------")

            if current_turn == 0:  # current turn is white
                if i % 2 != parent_turn:
                    continue
                if dtw[i] != current_distance - 1:
                    continue
                state_list = reverse_move(*num_to_state(i))
            else:  # current turn is black
                if dtw[i] != -1:
                    continue
                state_list = get_moved_states(*num_to_state(i))

            if current_turn == 0:  # white
                for j in state_list:
                    # ======================================= display =======================================
                    if node_cnt % 10000 == 0:
                        print(
                            f"**** overall expanded node number: {node_cnt}, distance: {current_distance}, (state number: {total_state_num}) ****")
                    node_cnt += 1
                    # ======================================= display =======================================
                    idx = state_to_num(j, current_turn)
                    if dtw[idx] == -1:
                        dtw[idx] = current_distance
                        par[idx] = i
            else:  # black
                better_option_for_black = -1
                black_best_state_num = -1
                for j in state_list:
                    # ======================================= display =======================================
                    if node_cnt % 10000 == 0:
                        print(
                            f"**** overall expanded node number: {node_cnt}, distance: {current_distance}, (state number: {total_state_num}) ****")
                    node_cnt += 1
                    # ======================================= display =======================================
                    state_num_of_j = state_to_num(j, 0)  # evaluate the state of white's turn
                    # if there is any option for black that is un-initilized, then this node has dtw more than current depth
                    if dtw[state_num_of_j] == -1:
                        better_option_for_black = -1
                        break
                    # otherwise
                    if dtw[state_num_of_j] > better_option_for_black:
                        better_option_for_black = dtw[state_num_of_j]
                        black_best_state_num = state_num_of_j
                if better_option_for_black == -1:
                    dtw[i] = current_distance
                    par[i] = black_best_state_num
        parent_turn = (parent_turn + 1) % 2
    # ----------- got all win states for white ----------------
    return dtw, par


def display(state2d, turn):
    dtw, par = optimal_strategy()
    # ======================================= display =======================================
    f = open("NxNoptimal_dtw.txt", "w+")
    f.write(str(dtw))
    f.close()
    g = open("NxNoptimal_par.txt", "w+")
    g.write(str(par))
    g.close()
    # ======================================= display =======================================
    states = []
    root = copy.deepcopy(state2d)
    reverse_color_flag = par[state_to_num(root, turn)]
    if reverse_color_flag == -2:  # un-initialized parent, so black win in optimal play
        for i in range(r):
            for j in range(c):
                if root[i][j] in [-1, 1]:
                    root[i][j] = - root[i][j]

    while True:
        sid = state_to_num(root, turn)
        sid = par[sid]
        root, turn = num_to_state(sid)
        root = [root[j * r:j * r + c] for j in range(r)]
        states.append(root)
        i = dtw[sid]
        if i == 0:
            break
    for i in states:
        for j in range(r):
            if reverse_color_flag == -2:  # we need to reverse color
                p = []
                for k in i[j]:
                    p.append(-k if k in [-1, 1] else k)
                print(p)
            else:
                print(i[j])
        print("-------------------")


# if __name__ == '__main__':
# print(side_combinations, position_combinations, obstacles_combinations, total_state_num)

piece_position_table, inv_piece_position_table = make_position_table(4, position_combinations, r * c)
side_position_table, inv_side_position_table = make_position_table(2, side_combinations, 4)
# display(config.init_chess_state, 0)
dtw, par = optimal_strategy()
