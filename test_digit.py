"""
>>>
"""

import pytest

from digits import Digit, ionized


@pytest.mark.parametrize(
    'value', range(10)
)
def test_eight_value(value):
    eight = Digit(value)
    assert eight.value == value
    assert eight.get_occupied() == Digit.occupied[value]


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
def test_len(value, length):
    digit = Digit(value)
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
    removals_values = {d.value for d in digit.ionized(1)}
    assert removals_values == removals


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
    removals_values = {d.value for d in digit.ionized(2)}
    assert removals_values == removals


@pytest.mark.parametrize(
    'occupied, value',
    [
        ((0, 1, 2, 3, 4, 5, 6), 8),
        ((0, 1, 2, 4, 5, 6), 0),
        ((0, 1, 2, 4, 5), None),
    ]
)
def test_from_occupied(occupied, value):
    digit = Digit.from_occupied(occupied)
    assert digit.get_occupied() == occupied
    assert digit.value == value


def test_pairs():
    pairs = [Digit(6), Digit(7)]
    assert ionized(pairs, n=1) == [
            [Digit(5), Digit(7)],
            [Digit(6), Digit(1)],
    ]
