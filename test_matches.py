from matches import Digit


def test_one():
    one = Digit(1)
    assert str(one) == """
 ──
│  ┃
 ──
│  ┃
 ──
"""


def test_two():
    two = Digit(2)
    assert str(two) == """
 ━━
│  ┃
 ━━
┃  │
 ━━
"""


def test_three():
    three = Digit(3)
    assert str(three) == """
 ━━
│  ┃
 ━━
│  ┃
 ━━
"""
