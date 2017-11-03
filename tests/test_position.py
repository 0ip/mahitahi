import pytest

from crdt.position import Position

BASE_BITS = 5


@pytest.mark.parametrize("pos_arr,base_bits,exp_pos_int", [
    ([1, 2], 1, 6),
    ([1, 2], 5, 66)
])
def test_to_int(pos_arr, base_bits, exp_pos_int):
    test_pos = Position(pos_arr, base_bits=base_bits)
    assert test_pos.to_int() == exp_pos_int


@pytest.mark.parametrize("pos_arr,trim,exp_pos_int", [
    ([1, 2], 1, 1),
    ([1, 2], 2, 66),
    ([1, 2], 3, 8448)
])
def test_to_int_with_trim(pos_arr, trim, exp_pos_int):
    test_pos = Position(pos_arr, base_bits=BASE_BITS)
    assert test_pos.to_int(trim=trim) == exp_pos_int


@pytest.mark.parametrize("left,right,depth,interval", [
    ([1, 2], [1, 3], 1, -1),
    ([1, 2], [1, 3], 2, 0),
    ([1, 2], [1, 4], 2, 1),
    ([1, 2], [1, 2, 1], 3, 0),
    ([1, 2], [1, 3], 3, 127)
])
def test_interval_between(left, right, depth, interval):
    p1, p2 = Position(left, base_bits=BASE_BITS), Position(right, base_bits=BASE_BITS)
    assert p1.interval_between(p2, depth) == interval


@pytest.mark.parametrize("left,right", [
    ([1, 2], [1, 2, 1]),
    ([1, 2], [1, 3])
])
def test_lt(left, right):
    assert left < right
