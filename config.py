GameName = 'chess'

GUI_ENABLE = True
# -- path
mct_simulate_num = 1

board_rows = 4
board_cols = 4
init_chess_state = [
    [0, 0, -1, 0],
    [-1, 0, 0, 0],
    [0, 0, 0, 1],
    [0, 0, 1, 0]
]
pick_piece_thrs = board_rows * board_cols * 8

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
