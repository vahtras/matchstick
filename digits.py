DIGIT_TEMPLATE = """
 {0}
{1}  {2}
 {3}
{4}  {5}
 {6}
"""


class Digit:
    occupied = {
    0: (0, 1, 2, 4, 5, 6),
    1: (2, 5),
    2: (0, 2, 3, 4, 6),
    3: (0, 2, 3, 5, 6),
    4: (1, 2, 3, 5),
    5: (0, 1, 3, 5, 6),
    6: (0, 1, 3, 4, 5, 6),
    7: (0, 2, 5),
    8: (0, 1, 2, 3, 4, 5, 6),
    9: (0, 1, 2, 3, 5, 6),
    }
    removals = {
        8: {0, 6, 9}
    }
    def __init__(self, value):
        self.value = value

    def __len__(self):
        return len(self.occupied[self.value])

    def removal_values(self):
        """
        tbd
        """
        return self.removals[self.value]

    def __repr__(self):
        matches = ['──', '│', '│', '──', '│', '│', '──']
        if self.value == 1:
            matches[2] = '┃'
            matches[5] = '┃'
        elif self.value == 2:
            matches[0] = '━━'
            matches[2] = '┃'
            matches[3] = '━━'
            matches[4] = '┃'
            matches[6] = '━━'
        elif self.value == 3:
            matches[0] = '━━'
            matches[2] = '┃'
            matches[3] = '━━'
            matches[5] = '┃'
            matches[6] = '━━'
        return DIGIT_TEMPLATE.format(*matches)
