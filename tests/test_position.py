import pytest

from crdt.position import Position


@pytest.mark.parametrize("pos_arr,base_bits,exp_pos_int", [
    ([1, 2], 1, 6),
    ([1, 2], 5, 66)
])
def test_to_int(pos_arr, base_bits, exp_pos_int):
    test_pos = Position(pos_arr)
    test_pos.BASE_BITS = base_bits
    assert test_pos.to_int() == exp_pos_int


@pytest.mark.parametrize("pos_arr,trim,exp_pos_int", [
    ([1, 2], 1, 1),
    ([1, 2], 2, 66),
    ([1, 2], 3, 8448)
])
def test_to_int_with_trim(pos_arr, trim, exp_pos_int):
    test_pos = Position(pos_arr)
    assert test_pos.to_int(trim=trim) == exp_pos_int
