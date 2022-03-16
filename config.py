GameName = 'chess'

GUI_ENABLE = True
# -- path
mct_simulate_num = 20
epsilon = 0.2
cpuct = 0.1  # mct cpuct
memory_size = 500
batch_size = 50
train_loop = 2
epochs = 3

# init_chess_state = [
#     [0, -1, 0],
#     [-1, 0, 1],
#     [0, 1, 0]
# ]

question_state = [
    [0, -1, 0, 0],
    [-1, 2, 1, 0],
    [0, 0, 0, 0],
    [0, 0, 1, 0]
]

# init_chess_state = [
#     [0, -1, 0, 0],
#     [-1, 0, 0, 1],
#     [0, 0, 1, 0]
# ]
#
# question_state = [
#     [0, -1, 0, 0],
#     [-1, 2, 1, 0],
#     [0, 0, 1, 0]
# ]

init_chess_state = [
    [0, -1, 0, 0],
    [-1, 0, 0, 0],
    [0, 0, 0, 1],
    [0, 0, 1, 0]
]

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
