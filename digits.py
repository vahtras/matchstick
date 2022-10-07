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
    occupied_reverse = {frozenset(v): k for k, v in occupied.items()}
    removals = {
        7: {1},
        8: {0, 6, 9},
        9: {3, 5},
    }

    def __init__(self, value):
        self.value = value

    def __len__(self):
        return len(self.occupied[self.value])

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return self.value

    def removal_values(self):
        """
        tbd
        """
        return self.removals[self.value]

    def _removals(self):
        return frozenset(Digit(n) for n in self.removals[self.value])

    def ionized(self, n=1):
        occupied = set(self.occupied[self.value])
        valid = set()
        if n == 1:
            for occ in occupied:
                if digit := Digit.from_occupied(occupied - {occ}):
                    valid.add(digit)
        if n == 2:
            for occa in occupied:
                for occb in occupied - {occa}:
                    if digit := Digit.from_occupied(
                        occupied - {occa} - {occb}
                    ):
                        valid.add(digit)
        return valid

    @classmethod
    def from_occupied(cls, occupied):
        value = cls.occupied_reverse.get(frozenset(occupied))
        if value is not None:
            return cls(value)

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
