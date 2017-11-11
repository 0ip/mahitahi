import pytest

from mahitahi.position import Position

BASE_BITS = 5


@pytest.mark.parametrize("pos,sites,base_bits,exp_pos_int", [
    ([1, 2], [0, 0], 1, 6),
    ([1, 2], [0, 0], 5, 66)
])
def test_to_int(pos, sites, base_bits, exp_pos_int):
    test_pos = Position(pos, sites, base_bits=base_bits)
    assert test_pos.to_int() == exp_pos_int


@pytest.mark.parametrize("pos,sites,trim,exp_pos_int", [
    ([1, 2], [0, 0], 1, 1),
    ([1, 2], [0, 0], 2, 66),
    ([1, 2], [0, 0], 3, 8448)
])
def test_to_int_with_trim(pos, sites, trim, exp_pos_int):
    test_pos = Position(pos, sites, base_bits=BASE_BITS)
    assert test_pos.to_int(trim=trim) == exp_pos_int


@pytest.mark.parametrize("left_pos,left_sites,right_pos,right_sites,depth,interval", [
    ([1, 2], [0, 0], [1, 2], [0, 0], 2, -1),
    ([1, 2], [0, 0], [1, 2], [0, 0], 3, -1),
    ([1, 2], [0, 0], [1, 3], [0, 0], 1, -1),
    ([1, 2], [0, 0], [1, 3], [0, 0], 2, 0),
    ([1, 2], [0, 0], [1, 4], [0, 0], 2, 1),
    ([1, 2], [0, 0], [1, 2, 1], [0, 0, 0], 3, 0),
    ([1, 2], [0, 0], [1, 3], [0, 0], 3, 127)
])
def test_interval_between(left_pos, left_sites, right_pos, right_sites, depth, interval):
    pos_1 = Position(left_pos, left_sites, base_bits=BASE_BITS)
    pos_2 = Position(right_pos, right_sites, base_bits=BASE_BITS)
    assert pos_1.interval_between(pos_2, depth) == (interval, False)


@pytest.mark.parametrize("left,right", [
    ([1, 2], [1, 2, 1]),
    ([1, 2], [1, 3])
])
def test_lt(left, right):
    assert left < right
