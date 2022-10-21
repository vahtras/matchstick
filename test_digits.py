import pathlib
import subprocess

import pytest

from digits import (
    token, Operator, Digit, move_matches, remove_matches, scan,
    valid_equations, img_filename, create_zip_with_symlink
)


@pytest.mark.parametrize(
    'value', range(10)
)
def test_eight_value(value):
    digit = Digit(value)
    assert digit.value == value
    assert digit.get_occupied() == Digit.occupied[value]


@pytest.mark.parametrize(
    'value', ['-', '+', '='],
)
def test_op_value(value):
    op = Operator(value)
    assert op.value == value
    assert op.get_occupied() == Operator.occupied[value]


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
def test_len_digit(value, length):
    digit = Digit(value)
    assert len(digit) == length


@pytest.mark.parametrize(
    'value, length',
    [
        ('-', 0),
        ('+', 1),
        ('=', 1),
    ]
)
def test_len_op(value, length):
    digit = Operator(value)
    assert len(digit) == length


@pytest.mark.parametrize(
    'value, valid_one_removed',
    [
        (0, set()),
        (7, {1}),
        (8, {0, 6, 9}),
        (9, {3, 5}),
    ]
)
def test_digit_removals(value, valid_one_removed):
    digit = Digit(value)
    assert digit.removal_values() == valid_one_removed


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
def test_digit_single_removals(value, removals):
    digit = Digit(value)
    removals_values = {d.value for d in digit.remove_matches(1)}
    assert removals_values == removals


@pytest.mark.parametrize(
    'value, removals',
    [
        ('-', set()),
        ('+', {'-'}),
        ('=', {'-'}),
    ]
)
def test_ops_single_removals(value, removals):
    op = Operator(value)
    removals_values = {d.value for d in op.remove_matches(1)}
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
def test_digit_single_additions(value, additions):
    digit = Digit(value)
    additions_values = {d.value for d in digit.add_matches(1)}
    assert additions_values == additions


@pytest.mark.parametrize(
    'value, additions',
    [
        ('-', {'+', '='}),
        ('+', set()),
        ('=', set()),
    ]
)
def test_op_single_additions(value, additions):
    op = Operator(value)
    additions_values = {d.value for d in op.add_matches(1)}
    assert additions_values == additions


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
def test_digit_single_excitations(value, excitations):
    digit = Digit(value)
    excitation_values = {d.value for d in digit.move_matches(1)}
    assert excitation_values == excitations


@pytest.mark.parametrize(
    'value, excitations',
    [
        ('-', set()),
        ('+', {'='}),
        ('=', {'+'}),
    ]
)
def test_opg_single_excitations(value, excitations):
    op = Operator(value)
    excitation_values = {d.value for d in op.move_matches(1)}
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
def test_digit_double_removals(value, removals):
    digit = Digit(value)
    removals_values = {d.value for d in digit.remove_matches(2)}
    assert removals_values == removals


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
def test_valid_equations(n, expected):
    equations = valid_equations(n)
    assert len(equations) == expected


@pytest.mark.parametrize(
    'eq, filename',
    [
        ('1 = 1', '1=1.png'),
        ('2 =1 ', '2=1.png'),
    ]
)
def test_img_filename(eq, filename):
    assert img_filename(eq) == filename


def test_zip_link():
    create_zip_with_symlink('cpuinfo.zip', 'cpuinfo.txt', '/proc/cpuinfo')
    subprocess.call('unzip cpuinfo.zip'.split())
    assert pathlib.Path('cpuinfo.txt').is_symlink
    # pathlib.Path('cpuinfo.txt').unlink
    # pathlib.Path('cpuinfo.zip').unlink
