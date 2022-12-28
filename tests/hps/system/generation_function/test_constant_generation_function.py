import pytest

from hps.system.generation_function import ConstantGenerationFunction


@pytest.fixture()
def gen_func():
    return ConstantGenerationFunction(
        p_min=50.0, p_max=100.0, power_equivalent=2.5
    )


def test_repr(gen_func):
    expected = "ConstantGenerationFunction(p_min=50.0, p_max=100.0, power_equivalent=2.5)"
    assert expected == gen_func.__repr__()


def test_min_generation(gen_func):
    assert gen_func.p_min == 50.0


def test_max_generation(gen_func):
    assert gen_func.p_max == 100.0


def test_min_discharge(gen_func):
    assert gen_func.q_min == 50.0/2.5


def test_max_discharge(gen_func):
    assert gen_func.q_max == 100.0/2.5


def test_power_equivalent(gen_func):
    assert gen_func.power_equivalent == 2.5
