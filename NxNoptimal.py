"""
turn: 0: white, 1: black
piece: -1: black, 0: space, 1: white, 2: obstacle
"""

import math

import config


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


def make_position_table(t, comb_num, limit):
    k = list(range(t))
    position_table = []
    for i in range(comb_num):
        position_table.append(k.copy())
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
    return position_table


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


def state_to_num(state, turn):
    pass


def reverse_move(state, turn):
    target_side = -1 if turn == 0 else 1
    state2d = [state[j * r:j * r + c] for j in range(r)]
    out = []
    return state2d


if __name__ == '__main__':
    print(side_combinations, position_combinations, obstacles_combinations, total_state_num)
    piece_position_table = make_position_table(4, position_combinations, r * c)
    side_position_table = make_position_table(2, side_combinations, 4)

    print(reverse_move(*num_to_state(total_state_num - 1)))
