import collections
import functools
import itertools
import pathlib
from PIL import Image
import tempfile
import stat
import zipfile


class Token:
    """
    Base class for matchstick patterns

    Each position in a pattern has a unique number
    An image is made up of matches occupying positions

    class variables

        occupied[dict]: maps matchstick image to occupations
        lookup_value[dict]: reverse lookup of occupied

    Below two subclasses are defined:
        Operator (+-=)
        Digit (0-9)


    """
    occupied = {}
    lookup_value = {}

    def __init__(self, value=None):
        """
        Initialize a token from value.

        >>> Digit(1)
        Digit(1)
        >>> Operator('+')
        Operator(+)
        """
        if value is not None:
            self._occupied = self.__class__.occupied.get(value)
        else:
            self._occupied = None

    @classmethod
    def from_occupied(cls, occupied):
        """
        Returns token with a given match positions

        >>> Digit.from_occupied((2, 5))
        Digit(1)
        >>> Operator.from_occupied(())
        Operator(-)
        """
        token = cls()
        token.set_occupied(occupied)
        return token

    def set_occupied(self, occupied):
        self._occupied = tuple(occupied)

    def get_occupied(self):
        return self._occupied

    def copy(self):
        return self.from_occupied(self._occupied)

    @property
    def value(self):
        return self.lookup_value.get(frozenset(self._occupied))

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
        return (
            f'{self.__class__.__name__}'
            f'({self.value if self.value is not None else self.get_occupied()})'
        )

    def remove_matches(self, n=1):
        """
        Return set of valid values after removing n digits

        >>> Digit(8).removal_values(n=1)
        {0, 6, 9}
        """
        if n > len(self):
            raise RemovalError

        valid = set()
        occupied = set(self._occupied)
        if n == 1:
            for occ in self._occupied:
                digit = self.__class__.from_occupied(occupied - {occ})
                if digit.value is not None:
                    valid.add(digit)
        if n == 2:
            for occa, occb in itertools.combinations(occupied, 2):
                digit = Digit.from_occupied(
                    occupied - {occa, occb}
                )
                if digit.value is not None:
                    valid.add(digit)
        return valid

    def add_matches(self, n=1):
        if len(self) + n > 7:
            raise AdditionError

        valid = set()
        occupied = set(self._occupied)
        virtual = set(range(7)) - occupied
        if n == 1:
            for vir in virtual:
                token = self.__class__.from_occupied(occupied | {vir})
                if token.value is not None:
                    valid.add(token)
        if n == 2:
            for vira, virb in itertools.combinations(virtual, 2):
                token = self.__class__.from_occupied(
                    occupied | {vira, virb}
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
            for occa, occb in itertools.combinations(occupied, 2):
                for vira, virb in itertools.combinations(virtual, 2):
                    token = self.__class__.from_occupied(
                        occupied - {occa, occb} | {vira, virb}
                    )
                    if token.value is not None:
                        valid.add(token)
        return valid


class Operator(Token):
    """
        0
     1 ━┃━
    """
    occupied = {
        '-': (),
        '+': (0,),
        '=': (1,),
    }
    lookup_value = {frozenset(v): k for k, v in occupied.items()}


class Digit(Token):
    """
    >>> Digit.occupied[8] # all matchstick positions occupied
    (0, 1, 2, 3, 4, 5, 6)

       0
       ━━
    1 ┃  ┃ 2
       ━━ 3
    4 ┃  ┃ 5
       ━━
       6

    """
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


def token(value):
    try:
        return Digit(int(value))
    except ValueError:
        if value in ('+-='):
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
    """
    Input list of tokens representing an equation,
    generate expressions by moving n matches from occupied to
    vacant sites

    """

    occupied = [(i, o) for i, t in enumerate(tokens) for o in t.get_occupied()]
    virtual = [(j, v) for j, t in enumerate(tokens) for v in t.get_virtual()]
    generated = set()

    if n == 1:
        """
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
        """


        for (i, occ), in itertools.combinations(occupied, r=1):
            hole = tokens[i].__class__.from_occupied(
                set(tokens[i].get_occupied()) - {occ}
            )
            tokens[i], ti = hole, tokens[i]
            for (j, vir), in itertools.combinations(virtual, r=1):
                particle = tokens[j].__class__.from_occupied(
                    set(tokens[j].get_occupied()) | {vir}
                )
                tokens[j], tj = particle, tokens[j]
                if all(t.value is not None for t in tokens):
                    generated.add(tuple(t.copy() for t in tokens))
                tokens[j] = tj
            tokens[i] = ti

    if n == 2:
        for (i1, occ1), (i2, occ2) in itertools.combinations(occupied, r=2):
            hole1 = tokens[i1].__class__.from_occupied(
                set(tokens[i1].get_occupied()) - {occ1}
            )
            tokens[i1], ti1 = hole1, tokens[i1]

            hole2 = tokens[i2].__class__.from_occupied(
                set(tokens[i2].get_occupied()) - {occ2}
            )
            tokens[i2], ti2 = hole2, tokens[i2]

            for (j1, vir1), (j2, vir2) in itertools.combinations(virtual, r=2):

                particle1 = tokens[j1].__class__.from_occupied(
                    set(tokens[j1].get_occupied()) | {vir1}
                )
                tokens[j1], tj1 = particle1, tokens[j1]

                particle2 = tokens[j2].__class__.from_occupied(
                    set(tokens[j2].get_occupied()) | {vir2}
                )
                tokens[j2], tj2 = particle2, tokens[j2]

                if all(d.value is not None for d in tokens):
                    generated.add(
                        tuple(d.copy() for d in tokens)
                    )
                tokens[j2] = tj2
                tokens[j1] = tj1

            tokens[i2] = ti2
            tokens[i1] = ti1

    return generated


def scan(expr):
    expr = expr.strip().replace(' ', '')
    tokens = [token(c) for c in expr]
    return tokens


def valid_equations(n):
    eqs = set()
    if n == 2:
        for n in range(10):
            eqs.add(f'{n} = {n}')
    if n == 3:
        for i in range(10):
            for j in range(10-i):
                eqs.add(f'{i} + {j} = {i+j}')
                eqs.add(f'{i} = {i+j} - {j}')
                eqs.add(f'{i+j} = {i} + {j}')
                eqs.add(f'{i+j} - {j} = {i}')
    if n == 4:
        for i in range(10):
            for j in range(10):
                for k in range(10):
                    for _l in range(10):
                        if i + j == k + _l:
                            eqs.add(f'{i} + {j} = {k} + {_l}')
                        if i - j == k + _l:
                            eqs.add(f'{i} - {j} = {k} + {_l}')
                        if i + j == k - _l:
                            eqs.add(f'{i} + {j} = {k} - {_l}')
                        if i - j == k - _l:
                            eqs.add(f'{i} - {j} = {k} - {_l}')
                        if i + j + k == _l:
                            eqs.add(f'{i} + {j} + {k} = {_l}')
                            eqs.add(f'{_l} = {i} + {j} + {k}')
                        if i - j + k == _l:
                            eqs.add(f'{i} - {j} + {k} = {_l}')
                            eqs.add(f'{_l} = {i} - {j} + {k}')
                        if i + j - k == _l:
                            eqs.add(f'{i} + {j} - {k} = {_l}')
                            eqs.add(f'{_l} = {i} + {j} - {k}')
                        if i - j - k == _l:
                            eqs.add(f'{i} - {j} - {k} = {_l}')
                            eqs.add(f'{_l} = {i} - {j} - {k}')

    return eqs


def map_solutions(n: int, m: int = 1) -> dict[str, set[str]]:
    """
    Given number of digits and number of moves return mapping of
    riddle to set of possible solutions

    >>> map_solutions(2):
    {"2 = 3": {"2 = 2", "3 = 3"}, ...}
    """
    eqs = valid_equations(n)
    solutions = collections.defaultdict(set)
    for eq in eqs:
        tokens = scan(eq)
        riddles = move_matches(tokens, m)
        for r in riddles:
            key = " ".join(str(token) for token in r)
            if is_trivial(key):
                continue
            if collections.Counter(key)['='] == 1:
                solutions[key].add(eq)
    return solutions


def generate_image(expr):
    expr = expr.strip().replace(' ', '')
    image_dir = pathlib.Path('img')
    images = [Image.open(image_dir/f'm{c}.jpg') for c in expr]
    images = [crop(image) for image in images]
    hsize = sum(image.size[0] for image in images)
    vsize = max(image.size[1] for image in images)
    mode = images[0].mode
    joined_image = Image.new(mode, (hsize, vsize))
    offset = 0
    for image in images:
        joined_image.paste(image, (offset, 0))
        offset += image.size[0]
    return joined_image


def crop(img, keep=300):
    width, height = img.size
    left = width//2 - keep//2
    right = width//2 + keep//2
    dim = (left, 0, right, height)
    imgc = img.crop(dim)
    return imgc


def img_filename(eq):
    eq = eq.strip().replace(' ', '')
    filename = f'{eq}.png'
    return filename


def is_trivial(expr):
    return eval(expr.replace('=', '==')) is True


def create_zip_with_symlink(output_zip_filename, link_source, link_target):

    with zipfile.ZipFile(
        output_zip_filename, 'w', compression=zipfile.ZIP_DEFLATED
    ) as zip_out:
        write_symlink_to_zip(zip_out, link_source, link_target)


def write_symlink_to_zip(zip_out, link_source, link_target):
    zip_info = zipfile.ZipInfo(link_source)
    zip_info.create_system = 3

    unix_st_mode = (
        stat.S_IFLNK | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
        stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP | stat.S_IROTH |
        stat.S_IWOTH | stat.S_IXOTH
    )

    zip_info.external_attr = unix_st_mode << 16
    zip_out.writestr(zip_info, link_target)


def zip_equalities(zip_file, equalities, path=None):
    zip_file = pathlib.Path(zip_file)
    if path is None:
        path = zip_file.stem
    with zipfile.ZipFile(zip_file, 'w') as zp:
        for eq in equalities:
            print(eq)
            img = generate_image(eq)
            filename = img_filename(eq)
            with tempfile.TemporaryDirectory() as td:
                tmp = pathlib.Path(td)
                img.save(tmp / filename)
                zp.write(
                    str(tmp/filename),
                    arcname=f'{path}/{filename}'
                )
        print(f'-> {zip_file}')


def zip_solutions(zip_file, mapping, path=None):
    zip_file = pathlib.Path(zip_file)
    if path is None:
        path = zip_file.stem
    equalities = functools.reduce(
        lambda x, y: x | y,
        (m[1] for m in mapping)
    )
    zip_equalities(zip_file, equalities, path=f'{path}/equalities')
    with zipfile.ZipFile(zip_file, 'a') as zp:
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            for riddle, solutions in mapping:
                print(f'{riddle}:\t', "\t".join(solutions))
                img_riddle = generate_image(riddle)
                img_riddle_filename = pathlib.Path(img_filename(riddle))
                riddle_dir = img_riddle_filename.stem
                img_riddle.save(tmp / img_riddle_filename)
                zp.write(
                    tmp/img_riddle_filename,
                    arcname=f'{path}/{len(solutions)}-solution-puzzles/{riddle_dir}/{img_riddle_filename}'
                )
                for solution in solutions:
                    img_solution_filename = img_filename(solution)
                    link = (
                        f'{path}/{len(solutions)}-solution-puzzles/{riddle_dir}/solutions/'
                        f'{img_solution_filename}'
                    )
                    target = f'../../../equalities/{img_solution_filename}'
                    print(f'ln -s {target} {link}')
                    write_symlink_to_zip(zp, link, target)
        print(f'-> {zip_file}')


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--single-moves', action='store_true',
        help='List valid single replacements of expression'
    )
    parser.add_argument(
        '--double-moves', action='store_true',
        help='List valid double replacements of expression'
    )
    parser.add_argument(
        '--list-equalities', action='store_true',
        help='List equalities of given dimension'
    )
    parser.add_argument(
        '--zip-equalities', action='store_true',
        help='Save equality images of given dimension as zip'
    )
    parser.add_argument(
        '--number-of-digits', default=2, type=int,
        help='Number of digits in expression'
    )
    parser.add_argument(
        '--number-of-moves', default=1, type=int,
        help='Number of matches moved'
    )

    parser.add_argument(
        '--map-solutions', action='store_true',
        help='Map riddle to solutions'
    )
    parser.add_argument(
        '--zip-solutions', action='store_true',
        help='Save riddle/solution images in zip file'
    )

    parser.add_argument(
        '--matchstick-image', action='store_true',
        help='Display matchstick image of expression'
    )

    args = parser.parse_args()

    if args.list_equalities:
        for eq in valid_equations(args.number_of_digits):
            print(eq)
    if args.zip_equalities:
        equations = valid_equations(args.number_of_digits)
        zip_file = f'equalities-{args.number_of_digits}.zip'
        zip_equalities(zip_file, equations)

    if args.map_solutions:
        mapping = map_solutions(args.number_of_digits, args.number_of_moves)
        mapping = sorted(mapping.items(), key=lambda x: (len(x[1]), x))
        for riddle, solutions in mapping:
            print(f'{riddle}:\t', "\t".join(solutions))

    if args.zip_solutions:
        zip_file = (
            f'{args.number_of_digits}-digit-{args.number_of_moves}-move-puzzles.zip'
        )

        equations = valid_equations(args.number_of_digits)
        zip_equalities(zip_file, equations)

        mapping = map_solutions(args.number_of_digits, args.number_of_moves)
        mapping = sorted(mapping.items(), key=lambda x: (len(x[1]), x))
        zip_solutions(zip_file, mapping)

    if args.single_moves:
        print("Move one matchstick in expression")
        while expr := input("Expression: "):
            tokens = scan(expr)
            moves = move_matches(tokens)
            print("Valid moves")
            for m in moves:
                print(" ".join(str(t) for t in m))

    if args.double_moves:
        print("Move two matchsticks in expression")
        while expr := input("Expression: "):
            tokens = scan(expr)
            moves = move_matches(tokens, n=2)
            print("Valid moves")
            for m in moves:
                print(" ".join(str(t) for t in m))

    if args.matchstick_image:
        print("Display matchstick image of expression:")
        while expr := input("Expression: "):
            img = generate_image(expr)
            img.show()


class RemovalError(Exception):
    pass

class AdditionError(Exception):
    pass
