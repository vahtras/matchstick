import pathlib
import subprocess

import pytest
from hypothesis import given
from hypothesis.strategies import integers

from digits import (
    token, Operator, Digit, move_matches, remove_matches, scan,
    valid_equations, img_filename, create_zip_with_symlink, is_trivial,
    map_solutions,
    RemovalError, AdditionError
)


class TestDigit:

    @pytest.mark.parametrize(
        'value', range(10)
    )
    def test_digit_value(self, value):
        """
        The instance is initialized with value
        and saved as a sequence of occpied match sites

        Retrieving the instance value by reverse lookup from occupied dictionary
        """
        digit = Digit(value)
        assert digit.value == value
        assert repr(digit) == f'Digit({value})'
        assert digit.get_occupied() == Digit.occupied[value]

    @pytest.mark.parametrize(
        'value, length',
        [
            (0, 6),
            (1, 2),
            (2, 5),
            (3, 5),
            (4, 4),
            (5, 5),
            (6, 6),
            (7, 3),
            (8, 7),
            (9, 6),
        ]
    )
    def test_len_digit(self, value, length):
        digit = Digit(value)
        assert len(digit) == length

    @pytest.mark.parametrize(
        'value, removals',
        [
            (0, set()),
            (1, set()),
            (2, set()),
            (3, set()),
            (4, set()),
            (5, set()),
            (6, {5}),
            (7, {1}),
            (8, {0, 6, 9}),
            (9, {3, 5}),
        ]
    )
    def test_digit_single_removals(self, value, removals):
        digit = Digit(value)
        removals_values = {d.value for d in digit.remove_matches(1)}
        assert removals_values == removals

    @pytest.mark.parametrize(
        'value, additions',
        [
            (0, {8}),
            (1, {7}),
            (2, set()),
            (3, {9}),
            (4, set()),
            (5, {6, 9}),
            (6, {8}),
            (7, set()),
            (8, set()),
            (9, {8}),
        ]
    )
    def test_digit_single_additions(self, value, additions):
        digit = Digit(value)
        if len(digit) <= 6:
            additions_values = {d.value for d in digit.add_matches(1)}
            assert additions_values == additions
        else:
            with pytest.raises(AdditionError):
                digit.add_matches(1)

    @pytest.mark.parametrize(
        'value, excitations',
        [
            (0, {6, 9}),
            (1, set()),
            (2, {3}),
            (3, {2, 5}),
            (4, set()),
            (5, {3}),
            (6, {0, 9}),
            (7, set()),
            (8, set()),
            (9, {0, 6}),
        ]
    )
    def test_digit_single_excitations(self, value, excitations):
        digit = Digit(value)
        excitation_values = {d.value for d in digit.move_matches(1)}
        assert excitation_values == excitations

    @pytest.mark.parametrize(
        'value, removals',
        [
            (0, set()),
            (1, set()),
            (2, set()),
            (3, {7}),
            (4, {1}),
            (5, set()),
            (6, set()),
            (7, set()),
            (8, {2, 3, 5}),
            (9, {4}),
        ]
    )
    def test_digit_double_removals(self, value, removals):
        digit = Digit(value)
        removals_values = {d.value for d in digit.remove_matches(2)}
        assert removals_values == removals

    @pytest.mark.parametrize(
        'value, additions',
        [
            (0, set()),
            (1, {4}),
            (2, {8}),
            (3, {8}),
            (4, {9}),
            (5, {8}),
            (6, set()),
            (7, {3}),
            (8, set()),
            (9, set()),
        ]
    )
    def test_digit_double_additions(self, value, additions):
        digit = Digit(value)
        if len(digit) <= 5:
            additions_values = {d.value for d in digit.add_matches(2)}
            assert additions_values == additions
        else:
            with pytest.raises(AdditionError):
                digit.add_matches(2)

    @pytest.mark.parametrize(
        'value, excitations',
        [
            (0, set()),
            (1, set()),
            (2, {5}),
            (3, set()),
            (4, set()),
            (5, {2}),
            (6, set()),
            (7, set()),
            (8, set()),
            (9, set()),
        ]
    )
    def test_digit_double_excitations(self, value, excitations):
        digit = Digit(value)
        excitation_values = {d.value for d in digit.move_matches(2)}
        assert excitation_values == excitations


class TestOp:

    @pytest.mark.parametrize(
        'value', ['-', '+', '='],
    )
    def test_operator_value(self, value):
        op = Operator(value)
        assert op.value == value
        assert repr(op) == f'Operator({value})'
        assert op.get_occupied() == Operator.occupied[value]

    @pytest.mark.parametrize(
        'value, length',
        [
            ('-', 0),
            ('+', 1),
            ('=', 1),
        ]
    )
    def test_len_op(self, value, length):
        digit = Operator(value)
        assert len(digit) == length

    @pytest.mark.parametrize(
        'value, removals',
        [
            ('-', set()),
            ('+', {'-'}),
            ('=', {'-'}),
        ]
    )
    def test_operator_single_removals(self, value, removals):
        op = Operator(value)
        if len(op):
            removals_values = {t.value for t in op.remove_matches(1)}
            assert removals_values == removals
        else:
            with pytest.raises(RemovalError):
                op.remove_matches(1)

    @pytest.mark.parametrize(
        'value, additions',
        [
            ('-', {'+', '='}),
            ('+', set()),
            ('=', set()),
        ]
    )
    def test_operator_single_additions(self, value, additions):
        op = Operator(value)
        additions_values = {d.value for d in op.add_matches(1)}
        assert additions_values == additions

    @pytest.mark.parametrize(
        'value, excitations',
        [
            ('-', set()),
            ('+', {'='}),
            ('=', {'+'}),
        ]
    )
    def test_operator_single_excitations(self, value, excitations):
        op = Operator(value)
        excitation_values = {d.value for d in op.move_matches(1)}
        assert excitation_values == excitations

    @pytest.mark.parametrize(
        'value, removals',
        [
            ('-', set()),
            ('+', set()),
            ('=', set()),
        ]
    )
    def test_operator_double_removals(self, value, removals):
        op = Operator(value)
        with pytest.raises(RemovalError):
            op.remove_matches(2)



@pytest.mark.parametrize(
    'occupied, value',
    [
        ((0, 1, 2, 3, 4, 5, 6), 8),
        ((0, 1, 2, 4, 5, 6), 0),
        ((0, 1, 2, 4, 5), None),
    ]
)
def test_digit_from_occupied(occupied, value):
    digit = Digit.from_occupied(occupied)
    assert digit.get_occupied() == occupied
    assert digit.value == value


@pytest.mark.parametrize(
    'occupied, value',
    [
        ((), '-'),
        ((0,), '+'),
        ((1,), '='),
    ]
)
def test_op_from_occupied(occupied, value):
    op = Operator.from_occupied(occupied)
    assert op.get_occupied() == occupied
    assert op.value == value


@pytest.mark.parametrize(
    'seq, expected',
    [
        ([Digit(6)], {(Digit(5),)}),
        ([Digit(7)], {(Digit(1),)}),
        ([Digit(6), Digit(7)], {(Digit(5), Digit(7)), (Digit(6), Digit(1))}),
        ([Operator('+')], {(Operator('-'),)}),
        (
            [Digit(6), Operator('+')],
            {(Digit(5), Operator('+')), (Digit(6), Operator('-'))}
        ),
    ]
)
def test_ionize_seq(seq, expected):
    assert remove_matches(seq, n=1) == expected


@pytest.mark.parametrize(
    'value, excitation_values',
    [
        (0, {6, 9}),
        (1, set()),
        (2, {3}),
        (3, {2, 5}),
        (4, set()),
        (5, {3}),
        (6, {0, 9}),
        (7, set()),
        (8, set()),
        (9, {0, 6}),
        ('-', set()),
        ('+', {'='}),
        ('=', {'+'}),
    ]
)
def test_excite_singles(value, excitation_values):
    singles = [token(value)]
    singles_excited = move_matches(singles)
    singles_excited_values = {s[0].value for s in singles_excited}
    assert singles_excited_values == excitation_values


@pytest.mark.skip
@pytest.mark.parametrize(
    'value, excitation_values',
    [
        (0, set()),
        (1, set()),
        (2, {5}),
        (3, set()),
        (4, set()),
        (5, {2}),
        (6, set()),
        (7, set()),
        (8, set()),
        (9, set()),
    ]
)
def test_doubly_excited_singles(value, excitation_values):
    singles = [token(value)]
    singles_excited = move_matches(singles, 2)
    singles_excited_values = {s[0].value for s in singles_excited}
    assert singles_excited_values == excitation_values

@pytest.mark.parametrize(
    'values, excitation_values',
    [
        ([0, 0], {(6, 0), (9, 0), (0, 6), (0, 9)}),
        ([0, 1], {(6, 1), (9, 1)}),
        ([0, 2], {(6, 2), (9, 2), (0, 3)}),
        ([0, 3], {(6, 3), (9, 3), (0, 2), (0, 5)}),
        ([0, 4], {(6, 4), (9, 4)}),
        ([0, 5], {(6, 5), (9, 5), (0, 3)}),
        ([0, 6], {(6, 6), (9, 6), (0, 0), (0, 9), (8, 5)}),
        ([0, 7], {(6, 7), (9, 7), (8, 1), }),
        ([0, 8], {(6, 8), (9, 8), (8, 0), (8, 9), (8, 6)}),
        ([0, 9], {(6, 9), (9, 9), (0, 0), (0, 6), (8, 3), (8, 5)}),
        ([1, 1], set()),
        ([1, 2], {(1, 3)}),
        ([1, 3], {(1, 2), (1, 5)}),
        ([1, 5], {(1, 3)}),
        ([1, 6], {(1, 0), (1, 9), (7, 5)}),
        ([1, 7], {(7, 1)}),
        ([1, 8], {(7, 0), (7, 6), (7, 9)}),
        ([1, 9], {(1, 0), (1, 6), (7, 3), (7, 5)}),
        ([2, 2], {(3, 2), (2, 3)}),
        ([2, 3], {(3, 3), (2, 2), (2, 5)}),
        ([2, 4], {(3, 4)}),
        ([2, 5], {(3, 5), (2, 3)}),
        ([2, 6], {(3, 6), (2, 0), (2, 9)}),
        ([2, 7], {(3, 7), }),
        ([2, 8], {(3, 8), }),
        ([2, 9], {(3, 9), (2, 0), (2, 6)}),
        ([3, 3], {(2, 3), (5, 3), (3, 2), (3, 5)}),
        ([3, 4], {(2, 4), (5, 4)}),
        ([3, 5], {(2, 5), (5, 5), (3, 3)}),
        ([3, 6], {(2, 6), (5, 6), (3, 0), (3, 9), (9, 5)}),
        ([3, 7], {(2, 7), (5, 7), (9, 1), }),
        ([3, 8], {(2, 8), (5, 8), (9, 0), (9, 6), (9, 9)}),
        ([3, 9], {(2, 9), (5, 9), (3, 0), (3, 6), (9, 3), (9, 5)}),
        ([4, 4], set()),
        ([4, 5], {(4, 3)}),
        ([4, 6], {(4, 0), (4, 9)}),
        ([4, 7], set()),
        ([4, 8], set()),
        ([4, 9], {(4, 0), (4, 6)}),
        ([5, 5], {(3, 5), (5, 3)}),
        ([5, 6], {(3, 6), (5, 0), (5, 9), (6, 5), (9, 5)}),
        ([5, 7], {(3, 7), (6, 1), (9, 1)}),
        ([5, 8], {(3, 8), (6, 0), (9, 0), (6, 6), (9, 6), (6, 9), (9, 9)}),
        ([5, 9], {(3, 9), (5, 0), (5, 6), (6, 3), (9, 3), (6, 5), (9, 5)}),
        ([6, 6], {(0, 6), (9, 6), (6, 0), (6, 9), (5, 8), (8, 5)}),
        ([6, 7], {(0, 7), (9, 7), (8, 1)}),
        ([6, 8], {(0, 8), (9, 8), (8, 0), (8, 6), (8, 9)}),
        ([6, 9], {(0, 9), (9, 9), (6, 0), (6, 6), (5, 8), (8, 3), (8, 5)}),
        ([7, 7], set()),
        ([7, 8], set()),
        ([7, 9], {(7, 0), (7, 6), (1, 8)}),
        ([8, 8], set()),
        ([8, 9], {(8, 0), (8, 6), (0, 8), (6, 8), (9, 8)}),
        (
            [9, 9],
            {(0, 9), (6, 9), (9, 0), (9, 6), (3, 8), (5, 8), (8, 3), (8, 5)}
        ),
        (['-'], set()),
        ([1, '='], {(1, '+'), (7, '-')}),
    ]
)
def test_excite_pairs(values, excitation_values):
    tokens = [token(v) for v in values]
    excited = move_matches(tokens)
    expected = {tuple(token(d) for d in seq) for seq in excitation_values}
    assert excited == expected


@pytest.mark.parametrize(
    'input, expected',
    [
        ('1', [Digit(1)]),
        ('12', [Digit(1), Digit(2)]),
        ('1 + 2', [Digit(1), Operator('+'), Digit(2)]),
    ]
)
def test_scan_tokens(input, expected):
    assert scan(input) == expected


@pytest.mark.parametrize(
    'n, expected',
    [
        (2, 10),
        (3, 220),
    ]
)
def test_valid_equation_count(n, expected):
    equations = valid_equations(n)
    assert len(equations) == expected


@given(integers(0, 9))
def test_valid_equations_2(n):
    assert f'{n} = {n}' in valid_equations(2)

@given(integers(0, 9), integers(0, 9))
def test_valid_equations_3(i, j):
    if i + j < 10:
        eqs = valid_equations(3)
        assert f'{i} + {j} = {i + j}' in eqs
        assert f'{i + j} = {i} + {j}' in eqs
        assert f'{i} = {i + j} - {j}' in eqs
        assert f'{i + j} - {j} = {i}' in eqs

@given(integers(0, 9), integers(0, 9), integers(0, 9))
def test_valid_equations_4(i, j, k):
    if i + j + k < 10:
        eqs = valid_equations(4)
        assert f'{i} + {j} + {k} = {i + j + k}' in eqs
        assert f'{i} + {j} = {i + j + k} - {k}' in eqs
        assert f'{i} = {i + j + k} - {j} - {k}' in eqs

        assert f'{i + j + k} = {i} + {j} + {k}' in eqs
        assert f'{i + j + k} - {k} = {i} + {j}' in eqs
        assert f'{i + j + k} - {j} - {k} = {i}' in eqs


@pytest.mark.parametrize(
    'eq, filename',
    [
        ('1 = 1', '1=1.png'),
        ('2 =1 ', '2=1.png'),
    ]
)
def test_img_filename(eq, filename):
    assert img_filename(eq) == filename


@pytest.mark.parametrize(
    'expr, expected',
    [
        ('0 = 0 + 0', True),
        ('1 = 0 + 0', False),
        ('1 = 2 + 0', False),
        ('1 + 2 + 0', False),
    ]
)
def test_trivial_cases(expr, expected):
    assert is_trivial(expr) is expected


def test_zip_link():
    create_zip_with_symlink('cpuinfo.zip', 'cpuinfo.txt', '/proc/cpuinfo')
    subprocess.call('unzip cpuinfo.zip'.split())
    assert pathlib.Path('cpuinfo.txt').is_symlink
    # pathlib.Path('cpuinfo.txt').unlink
    # pathlib.Path('cpuinfo.zip').unlink

def test_map_solutions():
    solutions = map_solutions(2, 1)
    assert solutions.get("2 = 3") == {"2 = 2", "3 = 3"}
