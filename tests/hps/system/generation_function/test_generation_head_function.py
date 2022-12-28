from hps.utils.function_approx import LinearFunctionApprox
import pytest

from hps.system.generation_function.generation_head_function import (
    BaseGenerationHeadFunction, VanillaGenerationHeadFunction)


@pytest.fixture()
def base_gen():
    return BaseGenerationHeadFunction(
        q_min=10, q_max=20, p_min=50.0, p_max=100.0
    )


@pytest.fixture()
def vanilla_gen():
    
    eff = LinearFunctionApprox(x=[10, 20,], y=[100, 100])
    return VanillaGenerationHeadFunction(
        q_min=10, q_max=20, p_min=50.0, p_max=100.0, eff=eff
    )


def test_constructor_signature(base_gen):
    assert base_gen.p_min == 50.0
    assert base_gen.p_max == 100.0
    assert base_gen.q_min == 10.0
    assert base_gen.q_max == 20.0


def test_get_power(vanilla_gen):
    assert vanilla_gen.eff.get_y(10) == 100

    discharge = 10
    head = 1000
    actual_power = vanilla_gen.get_power(discharge, head)

    exp_power = 1 * 1e3*9.81/1e6 * discharge * head
    assert actual_power == exp_power
    assert vanilla_gen.get_power(discharge=10, head=0) == 0.0


def test_return_null_when_discharge_below_min(vanilla_gen):
    assert vanilla_gen.get_power(discharge=9, head=1000) == 0.0


def test_repr(vanilla_gen):
    exp_repr = "eff = " + str(vanilla_gen.eff)+ "\n"
    exp_repr += "gen_func = "
    exp_repr += "VanillaGenerationHeadFunction(q_min=10.0, q_max=20.0, p_min=50.0, p_max=100.0, eff=eff)"
    actual_repr = str(vanilla_gen)

    assert exp_repr == actual_repr
