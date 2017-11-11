import pytest

from mahitahi.alloc import Allocator
from mahitahi.position import Position
from mahitahi.strategy import RandomStrategy

BASE_BITS = 5


@pytest.mark.parametrize("left_pos,left_sites,right_pos,right_sites,possible_pos", [
    ([0], [-1], [0, 1], [-1, 0], ([0, 0, 5], [0, 0, 123]))
])
def test_alloc(left_pos, left_sites, right_pos, right_sites, possible_pos):
    test_alloc = Allocator(RandomStrategy(), 0)
    p1 = Position(left_pos, left_sites, base_bits=BASE_BITS)
    p2 = Position(right_pos, right_sites, base_bits=BASE_BITS)

    assert test_alloc(p1, p2).pos in possible_pos
