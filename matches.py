"""
TBD
"""

DIGIT_TEMPLATE = """
 {0}
{1}  {2}
 {3}
{4}  {5}
 {6}
"""


class Digit:
    def __init__(self, value):
        self.value = value

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
        elif self.value == 4:
            matches[1] = '┃'
            matches[2] = '┃'
            matches[3] = '━━'
            matches[5] = '┃'
        elif self.value == 5:
            matches[0] = '━━'
            matches[1] = '┃'
            matches[3] = '━━'
            matches[5] = '┃'
            matches[6] = '━━'
        elif self.value == 6:
            matches[0] = '━━'
            matches[1] = '┃'
            matches[3] = '━━'
            matches[4] = '┃'
            matches[5] = '┃'
            matches[6] = '━━'
        elif self.value == 7:
            matches[0] = '━━'
            matches[2] = '┃'
            matches[5] = '┃'
        elif self.value == 8:
            matches[0] = '━━'
            matches[1] = '┃'
            matches[2] = '┃'
            matches[3] = '━━'
            matches[4] = '┃'
            matches[5] = '┃'
            matches[6] = '━━'
        elif self.value == 9:
            matches[0] = '━━'
            matches[1] = '┃'
            matches[2] = '┃'
            matches[3] = '━━'
            matches[5] = '┃'
            matches[6] = '━━'
        elif self.value == 0:
            matches[0] = '━━'
            matches[1] = '┃'
            matches[2] = '┃'
            matches[4] = '┃'
            matches[5] = '┃'
            matches[6] = '━━'

        return DIGIT_TEMPLATE.format(*matches)
