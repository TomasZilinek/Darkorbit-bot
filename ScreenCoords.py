import copy


class ScreenCoords:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return self.x + other.x, self.y + other.y

    def __sub__(self, other):
        return self.x - other.x, self.y - other.y

    def __mul__(self, other):
        return (x * other for x in self)

    def __setitem__(self, index, value):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value

    def __getitem__(self, index):
        return [self.x, self.y][index]

    def __iter__(self):
        self.n = 0
        self.max = 1
        return self

    def __next__(self):
        if self.n <= self.max:
            result = [self.x, self.y][self.n]
            self.n += 1
            return result
        else:
            raise StopIteration

    def set(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def horizontal_shift(self, x):
        cp = copy.deepcopy(self)
        cp.set(cp.x + x, cp.y)
        return cp

    def vertical_shift(self, y):
        cp = copy.deepcopy(self)
        cp.set(cp.x, cp.y + y)
        return cp

    def shift(self, x, y):
        return self.horizontal_shift(x).vertical_shift(y)
