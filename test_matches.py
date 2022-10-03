import pytest
from matches import Digit


@pytest.mark.parametrize(
    'n, digit',
    [
        (1, """
 ──
│  ┃
 ──
│  ┃
 ──
"""
         ),
        (2, """
 ━━
│  ┃
 ━━
┃  │
 ━━
"""
         ),
        (3, """
 ━━
│  ┃
 ━━
│  ┃
 ━━
"""
         ),
        (4, """
 ──
┃  ┃
 ━━
│  ┃
 ──
"""
         ),
    ],
    ids=[1, 2, 3, 4]
)
def test_digit(n, digit):
    assert str(Digit(n)) == digit
