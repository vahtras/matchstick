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
    eight = Digit(value)
    assert eight.value == value

def test_eight_len():
    eight = Digit(8)
    assert len(eight) == 7

def test_eight_removals():
    eight = Digit(8)
    assert eight.removal_values() == {0, 6, 9}
