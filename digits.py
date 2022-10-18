import collections
import pathlib
from PIL import Image
import tempfile
import zipfile


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
    return eqs


def map_solutions(n):
    eqs = valid_equations(n)
    solutions = collections.defaultdict(set)
    for eq in eqs:
        tokens = scan(eq)
        riddles = move_matches(tokens)
        for r in riddles:
            key = " ".join(str(token) for token in r)
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


def zip_equations(zip_file, equations):
    with zipfile.ZipFile(zip_file, 'w') as zp:
        for eq in equations:
            print(eq)
            eq = eq.strip().replace(' ', '')
            img_filename = f'{eq}.png'
            img = generate_image(eq)
            with tempfile.TemporaryDirectory() as td:
                tmp = pathlib.Path(td)
                img.save(tmp / img_filename)
                zp.write(str(tmp/img_filename), arcname=img_filename)
        print(f'-> {zip_file}')


def zip_solutions(zip_file, mapping):
    zip_file = pathlib.Path(zip_file)
    with zipfile.ZipFile(zip_file, 'w') as zp:
        with tempfile.TemporaryDirectory() as td:
            for riddle, solutions in mapping:
                print(f'{riddle}:\t', "\t".join(solutions))
                riddle = riddle.strip().replace(' ', '')
                img_riddle = generate_image(riddle)
                img_riddle_filename = f'{riddle}.png'
                tmp = pathlib.Path(td)
                img_riddle.save(tmp / img_riddle_filename)
                zp.write(
                    tmp/img_riddle_filename,
                    arcname=f'{zip_file.stem}/{riddle}/{img_riddle_filename}'
                )
                for solution in solutions:
                    solution = solution.strip().replace(' ', '')
                    img_solution = generate_image(solution)
                    img_solution_filename = f'{solution}.png'
                    img_solution.save(tmp / img_solution_filename)
                    zp.write(
                        tmp/img_solution_filename,
                        arcname=(
                            f'{zip_file.stem}/{riddle}/'
                            f'solutions/{img_solution_filename}'
                        )
                    )
        print(f'-> {zip_file}')


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--single-moves', action='store_true',
        help='List valid single replacements of expression'
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
        zip_equations(zip_file, equations)

    if args.map_solutions:
        mapping = map_solutions(args.number_of_digits)
        mapping = sorted(mapping.items(), key=lambda x: len(x[1]))
        for riddle, solutions in mapping:
            print(f'{riddle}:\t', "\t".join(solutions))

    if args.zip_solutions:
        mapping = map_solutions(args.number_of_digits)
        mapping = sorted(mapping.items(), key=lambda x: len(x[1]))
        zip_file = f'solutions-{args.number_of_digits}.zip'
        zip_solutions(zip_file, mapping)

    if args.single_moves:
        print("Move one matchstick in expression")
        while expr := input("Expression: "):
            tokens = scan(expr)
            moves = move_matches(tokens)
            print("Valid moves")
            for m in moves:
                print(" ".join(str(t) for t in m))

    if args.matchstick_image:
        print("Display matchstick image of expression:")
        while expr := input("Expression: "):
            img = generate_image(expr)
            img.show()
