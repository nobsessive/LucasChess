import copy


class Count:
    def __init__(self):
        self.val = 0
        self.next = 1
        self.mod = 10

    def incrs(self):
        self.val = (self.val + 1) % self.mod
        self.next = (self.next + 1) % self.mod


class GameSignal:
    def __init__(self, status, body, counter=0, trained_label=0):
        self.status = status  # 0 need action, -1 thinking
        self.body = body
        self.counter = counter  # training counter
        self.trained_label = trained_label

    def copy(self, gs):
        self.status = gs.status
        self.body = copy.deepcopy(gs.body)
        self.trained_label = gs.trained_label
        # self.counter=gs.counter
