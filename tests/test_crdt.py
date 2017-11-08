import pytest
import random

from copy import deepcopy

from crdt.crdt import CRDTDoc


def test_apply_patch_1():
    init_doc = CRDTDoc()
    init_doc.insert(0, "A")
    init_doc.insert(1, "B")
    init_doc.insert(2, "C")
    init_doc.insert(3, "\n")

    a_doc = deepcopy(init_doc)
    a_doc.site = 1
    patch_from_a = a_doc.insert(1, "x")

    assert a_doc.text == "AxBC\n"

    b_doc = deepcopy(init_doc)
    b_doc.site = 2
    patch_from_b = b_doc.delete(2)

    assert b_doc.text == "AB\n"

    a_doc.apply_patch(patch_from_b)

    assert a_doc.text == "AxB\n"

    b_doc.apply_patch(patch_from_a)

    assert b_doc.text == "AxB\n"


def test_apply_patch_2():
    init_doc = CRDTDoc()
    init_doc.site = 1
    init_doc.apply_patch('''{
        "op": "i",
        "char": "A",
        "pos": [1],
        "sites": [2],
        "clock": 1
    }''')

    init_doc.apply_patch('''{
        "op": "i",
        "char": "C",
        "pos": [1],
        "sites": [3],
        "clock": 1
    }''')

    init_doc.insert(1, "B")

    assert init_doc.text == "ABC"


def test_insert():
    test_str = "The quick brown fox jumps over the lazy dog"

    init_doc = CRDTDoc()

    for c in test_str:
        init_doc.insert(0, c)

    assert init_doc.text == test_str[::-1]
