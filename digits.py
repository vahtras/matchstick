class Digit:
    maps = {
        8: (0, 1, 2, 3, 4, 5, 6)
    }
    removals = {
        8: {0, 6, 9}
    }
    def __init__(self, value):
        self.value = value

    def __len__(self):
        return len(self.maps[self.value])

    def removal_values(self):
        return self.removals[self.value]
