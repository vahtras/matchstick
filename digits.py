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
    lookup_value = {frozenset(v): k for k, v in occupied.items()}
    removals = {
        7: {1},
        8: {0, 6, 9},
        9: {3, 5},
    }

    def __init__(self, value=None):
        if value is not None:
            self._occupied = Digit.occupied.get(value)
        else:
            self._occupied = None

    @property
    def value(self):
        return self.lookup_value.get(frozenset(self._occupied))

    def __len__(self):
        return len(self._occupied)

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return hash(self._occupied)

    def get_occupied(self):
        return self._occupied

    def set_occupied(self, occupied):
        self._occupied = tuple(occupied)

    def get_virtual(self):
        return set(range(7)) - set(self._occupied)

    def removal_values(self):
        values = set()
        for i, n in enumerate(self._occupied):
            occ = frozenset(set(self._occupied) - {n})
            if (d := Digit.lookup_value.get(occ)) is not None:
                values.add(d)
        return values

    def _removals(self):
        return frozenset(Digit(n) for n in self.removals[self.value])

    def ionized(self, n=1):
        valid = set()
        occupied = set(self._occupied)
        if n == 1:
            for occ in self._occupied:
                digit = Digit.from_occupied(occupied - {occ})
                if digit.value is not None:
                    valid.add(digit)
        if n == 2:
            for occa in occupied:
                for occb in occupied - {occa}:
                    digit = Digit.from_occupied(
                        occupied - {occa} - {occb}
                    )
                    if digit.value is not None:
                        valid.add(digit)
        return valid

    def anionized(self, n=1):
        valid = set()
        occupied = set(self._occupied)
        virtual = set(range(7)) - occupied
        if n == 1:
            for vir in virtual:
                digit = Digit.from_occupied(occupied | {vir})
                if digit.value is not None:
                    valid.add(digit)
        if n == 2:
            for occa in occupied:
                for occb in occupied - {occa}:
                    digit = Digit.from_occupied(
                        occupied - {occa} - {occb}
                    )
                    if digit.value is not None:
                        valid.add(digit)
        return valid

    def excitations(self, n=1):
        valid = set()
        occupied = set(self._occupied)
        virtual = set(range(7)) - occupied
        if n == 1:
            for occ in occupied:
                for vir in virtual:
                    digit = Digit.from_occupied(occupied - {occ} | {vir})
                    if digit.value is not None:
                        valid.add(digit)
        if n == 2:
            for occa in occupied:
                for occb in occupied - {occa}:
                    digit = Digit.from_occupied(
                        occupied - {occa} - {occb}
                    )
                    if digit.value is not None:
                        valid.add(digit)
        return valid

    @classmethod
    def from_occupied(cls, occupied):
        digit = Digit()
        digit.set_occupied(occupied)
        return digit

    def __repr__(self):
        return f'{self.value}'


def ionized(digits: list[Digit], n: int = 1):
    generated = []
    if n == 1:
        for i, d in enumerate(digits):
            for d_ in d.ionized(n):
                digits[i] = d_
                generated.append([Digit(d.value) for d in digits])
            digits[i] = d
    return generated


def excite(digits: list[Digit], n: int = 1):
    generated = set()
    if n == 1:
        for i, di in enumerate(digits):
            occupied_i = set(di.get_occupied())
            for j, dj in enumerate(digits):
                occupied_j = set(dj.get_occupied())
                virtual_j = set(dj.get_virtual())
                for occ in occupied_i:
                    for vir in virtual_j:
                        if i == j:
                            digits[i] = Digit.from_occupied(
                                occupied_i - {occ} | {vir}
                            )
                        else:
                            digits[i] = Digit.from_occupied(occupied_i - {occ})
                            digits[j] = Digit.from_occupied(occupied_j | {vir})

                        if all(d.value is not None for d in digits):
                            generated.add(
                                tuple(
                                    Digit.from_occupied(d._occupied)
                                    for d in digits
                                )
                            )
                        digits[j] = dj
                        digits[i] = di
    return generated
