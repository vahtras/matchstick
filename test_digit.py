"""
>>>
"""

import pytest

from digits import Digit


@pytest.mark.parametrize(
    'value',
    [
        (0,),
        (8,),
    ]
)
def test_eight_value(value):
    ">>>"
    eight = Digit(value)
    assert eight.value == value


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
    ">>> "
    digit = Digit(value)
    assert len(digit) == length


@pytest.mark.parametrize(
    'value, removals',
    [
        (7, {1}),
        (8, {0, 6, 9}),
    ]
)
def test_digit_removals(value, removals):
    digit = Digit(value)
    assert digit.removal_values() == removals


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
    ]
)
def test_from_occupied(occupied, value):
    digit = Digit.from_occupied(occupied)
    assert digit.value == value
