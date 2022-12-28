import pytest
from hps.utils.function_approx import LinearFunctionApprox
from hps.system.nodes import PowerStation
from hps.system.generation_function.base_generation_function import IGenerationFunction
from hps.system.generation_function import ConstantGenerationFunction
from hps.system.generation_function.generation_head_function import BaseGenerationHeadFunction, VanillaGenerationHeadFunction


@pytest.fixture()
def power_station():
    return PowerStation(name="ps1", start_cost=10.0, initial_state=False)


def test_name(power_station):
    assert power_station.name == "ps1"


def test_start_cost(power_station):
    assert power_station.start_cost == 10.0


def test_initial_state(power_station):
    assert not power_station.initial_state


def test_generation_function(power_station):
    assert isinstance(power_station.generation_function, IGenerationFunction)


def test_energy_equivalent_with_head():
    discharge = 18
    head = 850
    
    eff = LinearFunctionApprox(x=[10, 20,], y=[100.0, 100.0])
    gf =  VanillaGenerationHeadFunction(
        q_min=10, q_max=20, p_min=50.0, p_max=100.0, eff=eff
    )

    power = gf.get_power(discharge, head)
    energy_equivalent = power / (discharge * 3.6)

    ps = PowerStation("test", start_cost=3e3, initial_state=False, generation_function=gf,
        nominal_discharge=discharge, nominal_head=head)

    assert energy_equivalent == ps.energy_equivalent

def test_energy_equivalent():
    discharge = 18
    gf = ConstantGenerationFunction(
        p_min=40.0, p_max=100.0, power_equivalent=2.5
    )
    energy_eq = gf.get_power(discharge) / (discharge * 3.6)
    ps = PowerStation("test", start_cost=3e3, initial_state=False, generation_function=gf,
        nominal_discharge=discharge)

    assert ps.energy_equivalent == energy_eq