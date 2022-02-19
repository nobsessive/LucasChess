class GameSpecificCommand:
    def __init__(self):
        self.move = None


class chessaction:
    # -- action
    # [kind][color][piece number][move number]
    # [ 1-6][0-1  ][0-9         ][0-21       ]
    def __init__(self, kind=None, color=None, pc=None, mn=None):  # kind, color, piece name, move number
        self.a = [kind, color, pc, mn]


class chess:
    def __init__(self):
        self.current_step = 0
        self.state_path = []
        self.state_path.append(chessstate())

    def act(self, action):
        s = self.state_path[current_step]
        s.act(action)


class chessstate:
    def __init__(self):
        self.board = [
            [13, 14, 15, 12, 11, 15, 14, 13],
            [16, 16, 16, 16, 16, 16, 16, 16],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [6, 6, 6, 6, 6, 6, 6, 6],
            [3, 4, 5, 2, 1, 5, 4, 3]
        ]
        self.turn = 1  # white
        self.allowed_actions = self._gaa()

    def gaa(self):
        pass

    def act(self, action):
        if action in self.allowed_actions:
            self._take_action(action)
