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
def test_eight_len(value, length):
    ">>> "
    eight = Digit(value)
    assert len(eight) == length


def test_eight_removals():
    ">>> "
    eight = Digit(8)
    assert eight.removal_values() == {0, 6, 9}


def test_one():
    ">>> "
    one = Digit(1)
    expected = """
 ──
│  ┃
 ──
│  ┃
 ──
"""
    assert str(one) == expected


def test_two():
    ">>> "
    two = Digit(2)
    expected = """
 ━━
│  ┃
 ━━
┃  │
 ━━
"""
    assert str(two) == expected
