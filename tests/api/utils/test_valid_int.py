# -*- coding: utf-8 -*-

import pytest
from app.api.utils.helper import valid_int


def test_valid_int_01():
    myint = valid_int("123")
    assert myint == 123


def test_valid_int_02():
    with pytest.raises(ValueError) as e:
        valid_int("")

    with pytest.raises(ValueError) as e:
        valid_int(None)
