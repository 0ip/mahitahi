import pytest

from mahitahi.alloc import Allocator
from mahitahi.position import Position
from mahitahi.strategy import RandomStrategy

BASE_BITS = 5


@pytest.mark.parametrize("l_pos,l_sites,r_pos,r_sites,res_pos_u,res_pos_l,res_pos_depth", [
    ([0], [-1], [0, 1], [-1, 0], 5, 123, 3)
])
def test_alloc_pos(l_pos, l_sites, r_pos, r_sites, res_pos_u, res_pos_l, res_pos_depth):
    test_allocator = Allocator(RandomStrategy(), 0)
    p1 = Position(l_pos, l_sites, base_bits=BASE_BITS)
    p2 = Position(r_pos, r_sites, base_bits=BASE_BITS)

    int_at_depth = p1.interval_at(res_pos_depth)

    res_pos = test_allocator(p1, p2).pos

    assert 0 < res_pos[-1] <= res_pos_u or res_pos_l <= res_pos[-1] < int_at_depth
