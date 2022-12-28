import pytest

import numpy as np
from hps.system.head_function.base_head_function import (
    BaseHeadFunction, HeadFunction, LinearHeadFunction, ExpHeadFunction, ConstantHeadFunction)

from hps.utils import LinearFunctionApprox


@pytest.fixture()
def base_head():
    return BaseHeadFunction(
        lrv=50.0, hrv=100.0, v_min=0.0, v_max=100.
    )


@pytest.fixture()
def linear_head():
    return LinearHeadFunction(
        lrv=550, hrv=700, v_min=0, v_max=120)


@pytest.fixture()
def exp_head():
    return ExpHeadFunction(
        lrv=550, hrv=700, v_min=0, v_max=120, decay=0.04
    )


def test_signature(base_head):
    assert base_head.hrv == 100.0
    assert base_head.lrv == 50.0
    assert base_head.v_min == 0.0
    assert base_head.v_max == 100.


def test_linear_head_function(linear_head):
    assert linear_head.get_head(0.) == 550
    assert linear_head.get_head(120.) == 700
    assert linear_head.get_head(60.) == (700-550)/2 + 550

    with pytest.raises(ValueError):
        linear_head.get_head(-1)


def test_exp_head_function(exp_head):
    assert exp_head.get_head(0) == 550
    assert exp_head.get_head(120) == 700
    assert exp_head.get_head(60) == 687.0095380352645

    with pytest.raises(ValueError):
        exp_head.get_head(-1)


def test_constant_head():
    c_head = ConstantHeadFunction(210, 0, 100)

    exp_head = 210
    actual_head = c_head.get_head(10)

    assert exp_head == actual_head
    assert exp_head == c_head.lrv
    assert exp_head == c_head.hrv


def test_head_function():
    head_data = np.array([[0, 50], [100, 100]])
    func = LinearFunctionApprox(head_data[:, 0], head_data[:, 1])
    head = HeadFunction(50, 100, 0, 100, func)

    assert 50 == head.get_head(0)
    assert 75 == head.get_head(50)
    assert 100 == head.get_head(100)
