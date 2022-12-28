import pytest

import numpy as np

from hps.system.inflow import ScaleInflowModel, ScaleYearlyInflowModel
from hps.system.generation_function import ConstantGenerationFunction
from hps.system.head_function import ConstantHeadFunction

from hps.rl.environment.hscomponents import (
    Res, Spill, Station, StationAction, DischargeAction, VariableInflowAction, HSystem,
    PickGateAction)


@pytest.fixture()
def hydro_system():

    price_of_spillage=1

    #Reservoirs
    
    inflow_model = ScaleYearlyInflowModel(mean_yearly_inflow=200)
    head = ConstantHeadFunction(head=430, v_min=0, v_max=205)
    res1 = Res(name="res1", min_volume=0.000000000, max_volume=205.000000000, init_volume=100.000000000, end_volume=100.000000000, spillage=None, inflow_model=inflow_model, is_ocean=False, head=head, energy_equivalent=0.9429626538850028)

    ocean = Res(name="ocean", min_volume=0.000000000, max_volume=10000.000000000, init_volume=0.000000000, end_volume=0.000000000, spillage=None, inflow_model=inflow_model, is_ocean=True, head=None, energy_equivalent=None)

    res1.spillage = Spill("1-", ocean, price_of_spillage)

    #Stations
    gen_func = ConstantGenerationFunction(p_min=14, p_max=30, power_equivalent=2.5)
    ps1 = Station(name="ps1", minimum=17.779674276, maximum=53.339022829, gen_func=gen_func,energy_equivalent=0.9429626538850028)

    #Actions
    inflow_res1 = VariableInflowAction(name="inflow_res1", res=res1, yearly_inflow=200.000000000)
    res1_ps1_ocean = StationAction(name="res1_ps1_ocean", upper_res=res1, station=ps1, lower_res=ocean)
    
    reservoirs = [res1, ocean]
    stations = [ps1]
    actions = [inflow_res1, res1_ps1_ocean]

    return HSystem(reservoirs=reservoirs, stations=stations, sorted_actions=actions)


@pytest.fixture()
def station_action():
    upper_head = ConstantHeadFunction(head=100, v_min=0, v_max=10)
    upper_res = Res("res1", 0, 10, 5, 5, spillage=None, head=upper_head)
    gen_func = ConstantGenerationFunction(15, 30, 1.0)
    station = Station("ps1", 15, 30, gen_func=gen_func, energy_equivalent=1.0)
    lower_head = ConstantHeadFunction(head=50, v_min=0, v_max=12)
    lower_res = Res("res2", 0, 12, 5, 5, spillage=None, head=lower_head)
    
    ocean = Res("ocean",0,1E6,0,0,None,None,is_ocean=True)
    upper_res.spillage = Spill("sp1", lower_res, price_of_spillage=1)
    lower_res.spillage = Spill("sp2", ocean, price_of_spillage=1)
    return StationAction(
        name="StationAction1",
        upper_res=upper_res,
        station=station,
        lower_res=lower_res
    )

@pytest.fixture()
def discharge_action():
    upper_head = ConstantHeadFunction(head=100, v_min=0, v_max=10)
    upper_res = Res("res1", 0, 10, 5, 5, spillage=None, head=upper_head)
    
    lower_head = ConstantHeadFunction(head=50, v_min=0, v_max=12)
    lower_res = Res("res2", 0, 12, 5, 5, spillage=None, head=lower_head)
    
    ocean = Res("ocean",0,1E6,0,0,None,None,is_ocean=True)
    upper_res.spillage = Spill("sp1", lower_res, price_of_spillage=1)
    lower_res.spillage = Spill("sp2", ocean, price_of_spillage=1)
    return DischargeAction(
        name="DischargeAction1",
        upper_res=upper_res,
        lower_res=lower_res,
        max_flow=30
    )

@pytest.mark.parametrize(
    "discharge, price, step_size, exp_reward",
    [
        (10, 25, 30, 0.), # Below min prod
        (15, 25, 30, 11250.), # At min prod
        (30, 10,  1, 300.), # At max prod
        (40, 10,  1, 300.), # Over max prod
    ],
)
def test_station_action_execute(station_action, discharge, price, step_size, exp_reward):
    reward = station_action.execute(discharge, price, step_size)
    assert reward == exp_reward


def test_action_spillage_above(station_action, discharge_action):
    station_action.upper_res.current_volume = 15
    discharge, price, step_size = 15, 25, 100/3.6
    reward = station_action.execute(discharge, price, step_size)
    assert abs(reward - 10416.666667) < 1.e-4
    assert station_action.lower_res.current_volume == 5 + 1.5 + 3.5  # (curr + discharge_above + spillage_above)

    discharge_action.upper_res.current_volume = 15
    reward = discharge_action.execute(discharge, price, step_size)
    assert reward == 0.0
    assert discharge_action.lower_res.current_volume == 5. + 5.

def test_action_spillage_above_and_below(station_action, discharge_action):
    station_action.upper_res.current_volume = 15
    station_action.lower_res.current_volume = 12
    discharge, price, step_size = 15, 25, 100/3.6
    reward = station_action.execute(discharge, price, step_size)
    assert abs(reward - 10416.666667) < 1.e-4
    assert station_action.lower_res.current_volume == 17  # (curr + discharge_above + spillage_above) 

    discharge_action.upper_res.current_volume = 15
    discharge_action.lower_res.current_volume = 12
    reward = discharge_action.execute(discharge, price, step_size)
    assert reward == 0.0
    assert discharge_action.lower_res.current_volume == 17  # (curr + discharge_above + spillage_above) 

    
def test_spillage_above(station_action, discharge_action):
    station_action.upper_res.current_volume = 15
    
    discharge, price, step_size = 15, 25, 100/3.6
    reward = station_action.execute(discharge, price, step_size)

    spillage_reward = station_action.upper_res.spillage.execute(1.0)
    assert spillage_reward == -3.5*10**3
    assert station_action.upper_res.spillage.value == 3.5

    
    discharge_action.upper_res.current_volume = 15
    
    reward = discharge_action.execute(discharge, price, step_size)

    spillage_reward = discharge_action.upper_res.spillage.execute(1.0)
    assert spillage_reward == -3.5*10**3
    assert discharge_action.upper_res.spillage.value == 3.5

    

@pytest.fixture()
def h_system_gate_action():
    
    res1 = Res("res1", 0, 10, 5, 5, spillage=None, head=ConstantHeadFunction(head=100, v_min=0, v_max=10), energy_equivalent=1.)
    res2 = Res("res2", 0, 10, 5, 5, spillage=None, head=ConstantHeadFunction(head=100, v_min=0, v_max=10), energy_equivalent=1.)
    res3 = Res("res3", 0, 10, 5, 5, spillage=None, head=ConstantHeadFunction(head=100, v_min=0, v_max=10), energy_equivalent=0.)
    ocean = Res("ocean", 0, 1E5, 0, 0, spillage=None, is_ocean=True)

    res1.spillage = Spill("sp1", res3, 1)
    res2.spillage = Spill("sp2", res3, 1)
    res3.spillage = Spill("sp3", ocean, 1)

    gen_func = ConstantGenerationFunction(15, 30, 1.0)
    ps = Station("ps", 15, 30, gen_func=gen_func, energy_equivalent=1.0)
    
    res1_ps_res3 = StationAction("saction1", res1, ps, res3)
    res2_ps_res3 = StationAction("saction2", res2, ps, res3)

    inflow1 = VariableInflowAction("inf1", res1, yearly_inflow=10)
    inflow2 = VariableInflowAction("inf2", res1, yearly_inflow=10)
    inflow3 = VariableInflowAction("inf3", res1, yearly_inflow=10)

    gate_action = PickGateAction(name="Switch", input_actions=[res1_ps_res3, res2_ps_res3])
    return HSystem(reservoirs=[res1, res2, res3, ocean], stations=[ps], sorted_actions=[gate_action])


@pytest.fixture()
def h_system_three_gate_action():
    
    res1 = Res("res1", 0, 10, 5, 5, spillage=None, head=ConstantHeadFunction(head=100, v_min=0, v_max=10), energy_equivalent=1.)
    res2 = Res("res2", 0, 10, 5, 5, spillage=None, head=ConstantHeadFunction(head=100, v_min=0, v_max=10), energy_equivalent=1.)
    res3 = Res("res3", 0, 10, 5, 5, spillage=None, head=ConstantHeadFunction(head=100, v_min=0, v_max=10), energy_equivalent=0.)
    ocean = Res("ocean", 0, 1E5, 0, 0, spillage=None, is_ocean=True)

    res1.spillage = Spill("sp1", ocean, 1)
    res2.spillage = Spill("sp2", ocean, 1)
    res3.spillage = Spill("sp3", ocean, 1)

    gen_func = ConstantGenerationFunction(15, 30, 1.0)
    ps = Station("ps", 15, 30, gen_func=gen_func, energy_equivalent=1.0)
    
    res1_ps = StationAction("saction1", res1, ps, ocean)
    res2_ps = StationAction("saction2", res2, ps, ocean)
    res3_ps = StationAction("saction3", res3, ps, ocean)

    inflow1 = VariableInflowAction("inf1", res1, yearly_inflow=10)
    inflow2 = VariableInflowAction("inf2", res1, yearly_inflow=10)
    inflow3 = VariableInflowAction("inf3", res1, yearly_inflow=10)
    gate_action = PickGateAction(name="Switch", input_actions=[res1_ps, res2_ps, res3_ps])

    return HSystem(reservoirs=[res1, res2, res3, ocean], stations=[ps], sorted_actions=[gate_action])


def test_get_num_actions_for_pick_gate_action(h_system_gate_action):
    expected_n_actions = 2 + 1 # Two station actions + gate decision action
    actual_n_actions = h_system_gate_action.get_num_actions()
    assert actual_n_actions == expected_n_actions


@pytest.mark.skip("To be implemented")
def test_execute_for_pick_gate_action(h_system_gate_action):
    
    in_norm_actions = np.array([0.5, 0.7, 0.6])
    step_size = 1
    scaled_price = 12
    scaled_mean_price = scaled_price
    is_last_step = False
    inflows = {}
    for res in h_system_gate_action.reservoirs:
        inflows[res.name] = 0.
    
    reward = h_system_gate_action.execute(
        in_norm_actions, step_size, scaled_price, inflows)
     
    assert h_system_gate_action.reservoirs[0].current_volume == 5
    assert h_system_gate_action.reservoirs[1].current_volume ==  5 - 30*1*3600/1e6
    assert h_system_gate_action.reservoirs[2].current_volume ==  5 + 30*1*3600/1e6
    assert h_system_gate_action.stations[0].production == 30
    assert reward == 30.*12


def test_execute_for_pick_gate_action_with_spillage(h_system_gate_action):
    
    in_norm_actions = np.array([0.5, 0.2, 0.6])
    step_size = 1
    scaled_price = 12
    scaled_mean_price = scaled_price
    is_last_step = False
    inflows = {}
    
    h_system_gate_action.reservoirs[0].current_volume = 5
    h_system_gate_action.reservoirs[1].current_volume = 12
    h_system_gate_action.reservoirs[2].current_volume = 5
    
    reward = h_system_gate_action.execute(
        in_norm_actions, step_size, scaled_price, inflows)
     
    discharge_vol = ((0.5 - 0.3)/(0.7 - 0.3)*15 + 15)*1*3600/1e6
    spillage_res2_res3 = 2
    assert h_system_gate_action.reservoirs[0].current_volume == 5 - discharge_vol
    assert h_system_gate_action.reservoirs[1].current_volume ==  10
    assert h_system_gate_action.reservoirs[2].current_volume ==  5 + discharge_vol + spillage_res2_res3
    assert h_system_gate_action.stations[0].production == 22.5
    assert reward == 270. - 1*spillage_res2_res3*1*10**3


@pytest.mark.skip("To be implemented")
def test_execute_for_pick_three_gate_action_with_spillage(h_system_three_gate_action):
    
    in_norm_actions = np.array([0.5, 0.2, 0.4, 0.6])
    step_size = 1
    scaled_price = 12
    scaled_mean_price = scaled_price
    is_last_step = False
    inflows = {}
    
    h_system_three_gate_action.reservoirs[0].current_volume = 5
    h_system_three_gate_action.reservoirs[1].current_volume = 12
    h_system_three_gate_action.reservoirs[2].current_volume = 5
    
    reward = h_system_three_gate_action.execute(
        in_norm_actions, step_size, scaled_price, inflows)
     
    discharge_vol = ((0.5 - 0.3)/(0.7 - 0.3) * 15 + 15) * 1 * 3600 / 1e6
    spillage_res2_res3 = 2
    assert h_system_three_gate_action.reservoirs[0].current_volume == 5 - discharge_vol
    assert h_system_three_gate_action.reservoirs[1].current_volume ==  10
    assert h_system_three_gate_action.reservoirs[2].current_volume ==  5 + discharge_vol + spillage_res2_res3
    assert h_system_three_gate_action.stations[0].production == 22.5
    assert reward == 270. - 1*spillage_res2_res3*1*10**3