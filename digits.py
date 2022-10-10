DIGIT_TEMPLATE = """
 {0}

 {3}
{4}  {5}
 {6}
"""


class Token:
    occupied = {}
    lookup_value = {}

    def __init__(self, value=None):
        if value is not None:
            self._occupied = self.__class__.occupied.get(value)
        else:
            self._occupied = None

    @classmethod
    def from_occupied(cls, occupied):
        token = cls()
        token.set_occupied(occupied)
        return token

    def set_occupied(self, occupied):
        self._occupied = tuple(occupied)

    @property
    def value(self):
        return self.lookup_value.get(frozenset(self._occupied))

    def get_occupied(self):
        return self._occupied

    def get_virtual(self):
        return set(range(7)) - set(self._occupied)

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return hash(self._occupied)

    def __len__(self):
        return len(self._occupied)

    def __str__(self):
        return f'{self.value}'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.value})'

    def remove_matches(self, n=1):
        valid = set()
        occupied = set(self._occupied)
        if n == 1:
            for occ in self._occupied:
                digit = self.__class__.from_occupied(occupied - {occ})
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

    def add_matches(self, n=1):
        valid = set()
        occupied = set(self._occupied)
        virtual = set(range(7)) - occupied
        if n == 1:
            for vir in virtual:
                token = self.__class__.from_occupied(occupied | {vir})
                if token.value is not None:
                    valid.add(token)
        if n == 2:
            for occa in occupied:
                for occb in occupied - {occa}:
                    token = self.__class__.from_occupied(
                        occupied - {occa} - {occb}
                    )
                    if token.value is not None:
                        valid.add(token)
        return valid

    def move_matches(self, n=1):
        valid = set()
        occupied = set(self._occupied)
        virtual = set(range(7)) - occupied
        if n == 1:
            for occ in occupied:
                for vir in virtual:
                    token = self.__class__.from_occupied(
                        occupied - {occ} | {vir}
                    )
                    if token.value is not None:
                        valid.add(token)
        if n == 2:
            for occa in occupied:
                for occb in occupied - {occa}:
                    token = self.__class__.from_occupied(
                        occupied - {occa} - {occb}
                    )
                    if token.value is not None:
                        valid.add(token)
        return valid


class Operator(Token):
    occupied = {
        '-': (),
        '+': (0,),
        '=': (1,),
    }
    lookup_value = {frozenset(v): k for k, v in occupied.items()}


class Digit(Token):
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

    def removal_values(self):
        values = set()
        for i, n in enumerate(self._occupied):
            occ = frozenset(set(self._occupied) - {n})
            if (d := Digit.lookup_value.get(occ)) is not None:
                values.add(d)
        return values


def token(value):
    if isinstance(value, int):
        return Digit(value)
    elif value in ('+-='):
        return Operator(value)
    else:
        raise ValueError


def remove_matches(tokens: list[Token], n: int = 1):
    generated = set()
    if n == 1:
        for i, d in enumerate(tokens):
            for d_ in d.remove_matches(n):
                tokens[i] = d_
                if all(t.value is not None for t in tokens):
                    generated.add(tuple(d.__class__(d.value) for d in tokens))
                tokens[i] = d
    return generated


def move_matches(tokens: list[Token], n: int = 1):
    generated = set()
    if n == 1:
        for i, di in enumerate(tokens):
            cli = di.__class__
            occupied_i = set(di.get_occupied())
            for j, dj in enumerate(tokens):
                occupied_j = set(dj.get_occupied())
                clj = dj.__class__
                virtual_j = set(dj.get_virtual())
                for occ in occupied_i:
                    for vir in virtual_j:
                        if i == j:
                            tokens[i] = cli.from_occupied(
                                occupied_i - {occ} | {vir}
                            )
                        else:
                            tokens[i] = cli.from_occupied(occupied_i - {occ})
                            tokens[j] = clj.from_occupied(occupied_j | {vir})

                        if all(d.value is not None for d in tokens):
                            generated.add(
                                tuple(
                                    d.__class__.from_occupied(d._occupied)
                                    for d in tokens
                                )
                            )
                        tokens[j] = dj
                        tokens[i] = di
    return generated
