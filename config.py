GameName = 'chess'

GUI_ENABLE = True
# -- path
mct_simulate_num = 60
epsilon = 0.3
cpuct = 0.7  # mct cpuct

# board_rows = 3
# board_cols = 3
init_chess_state = [
    [0, -1, 0],
    [-1, 0, 1],
    [0, 1, 0]
]
# question_state = [
#     [0, -1, 0],
#     [2, 1, 2],
#     [-1, 1, 0]
# ]


# init_chess_state = [
#     [0, -1, 0, 0],
#     [-1, 0, 0, 0],
#     [0, 0, 0, 1],
#     [0, 0, 1, 0]
# ]


# board_rows=6
# board_cols=6
# init_chess_state=[
#             [0, 0, 0, -1, 0, 0],
#             [0, 0, 0, 0, 0, 0],
#             [-1, 0, 0, 0, 0, 0],
#             [0, 0, 0, 0, 0, 1],
#             [0, 0, 0, 0, 0, 0],
#             [0, 0, 1, 0, 0, 0]
#         ]

board_rows = len(init_chess_state)
board_cols = len(init_chess_state[0])

pick_piece_thrs = board_rows * board_cols * 8
