"""Module containing tests for the HydroSystem class."""

import pytest

from hps import HydroSystem
from hps import Reservoir, PowerStation, Creek, Gate, Ocean
from hps import Discharge, Spillage, Bypass


@pytest.fixture()
def empty_hydro_system():
    return HydroSystem()


@pytest.fixture()
def dummy_hydro_system(empty_hydro_system):
    res1 = Reservoir("res1", min_volume=0, max_volume=12)
    res2 = Reservoir("res2", min_volume=0, max_volume=12)
    dis = Discharge(res1, res2)
    spi = Spillage(res1, res2)
    byp = Bypass(res1, res2)

    empty_hydro_system.add_nodes_from([res1, res2])
    empty_hydro_system.add_edges_from([dis, spi, byp])

    return empty_hydro_system

def test_get_subgraph(dummy_hydro_system):
    sub_hs = dummy_hydro_system.get_subgraph(Discharge)

    assert sub_hs.discharges == dummy_hydro_system.discharges
    assert sub_hs.my_edges == sub_hs.discharges

def test_initialize_hydro_system():
    res1 = Reservoir("res1", min_volume=0, max_volume=12)
    res2 = Reservoir("res2", min_volume=0, max_volume=12)

    dis = Discharge(res1, res2)

    hydsys = HydroSystem(nodes=[res1, res2], edges=[dis])

    assert hydsys.my_nodes == [res1, res2]
    assert hydsys.my_edges == [dis]


def test_empty_system(empty_hydro_system):
    assert empty_hydro_system.my_edges == []
    assert empty_hydro_system.my_nodes == []


def test_add_edge_not_in_system(empty_hydro_system):
    res1 = Reservoir("res1", min_volume=0, max_volume=12)
    res2 = Reservoir("res2", min_volume=0, max_volume=12)

    dis = Discharge(res1, res2)

    with pytest.raises(ValueError):
        empty_hydro_system.add_edges_from([dis])


def test_add_nodes(empty_hydro_system):
    res = Reservoir("res2", min_volume=0, max_volume=12)
    creek = Creek("creek")
    ocean = Ocean("sjø")
    ps1 = PowerStation("ps", 1e3, False)
    gate = Gate("switch")

    empty_hydro_system.add_nodes_from([res, creek, ocean, ps1, gate])

    assert empty_hydro_system.my_nodes == [res, creek, ocean, ps1, gate]
    assert empty_hydro_system.reservoirs == [res]
    assert empty_hydro_system.oceans == [ocean]
    assert empty_hydro_system.power_stations == [ps1]
    assert empty_hydro_system.gates == [gate]
    assert empty_hydro_system.creeks == [creek]


def test_add_nodes_fails_for_non_valid_type(empty_hydro_system):
    with pytest.raises(ValueError):
        empty_hydro_system.add_nodes_from([2])


def test_add_edges(empty_hydro_system):
    res1 = Reservoir("res1", min_volume=0, max_volume=12)
    res2 = Reservoir("res2", min_volume=0, max_volume=12)
    dis = Discharge(res1, res2)
    spi = Spillage(res1, res2)
    byp = Bypass(res1, res2)

    empty_hydro_system.add_nodes_from([res1, res2])
    empty_hydro_system.add_edges_from([dis, spi, byp])

    assert empty_hydro_system.my_edges == [dis, spi, byp]
    assert empty_hydro_system.spillages == [spi]
    assert empty_hydro_system.bypasses == [byp]
    assert empty_hydro_system.discharges == [dis]


def test_add_reservoir(empty_hydro_system):
    res = Reservoir("res1", min_volume=0, max_volume=12)
    empty_hydro_system.add_node(res)
    assert empty_hydro_system.reservoirs == [res]
    assert empty_hydro_system.my_nodes == [res]


def test_add_power_station(empty_hydro_system):
    ps1 = PowerStation("ps1", 1e3, False)
    empty_hydro_system.add_node(ps1)
    assert empty_hydro_system.power_stations == [ps1]
    assert empty_hydro_system.my_nodes == [ps1]


def test_add_creek(empty_hydro_system):
    creek = Creek("creek")
    empty_hydro_system.add_node(creek)
    assert empty_hydro_system.creeks == [creek]
    assert empty_hydro_system.my_nodes == [creek]


def test_add_ocean(empty_hydro_system):
    ocean = Ocean("ocean")
    empty_hydro_system.add_node(ocean)
    assert empty_hydro_system.oceans == [ocean]
    assert empty_hydro_system.my_nodes == [ocean]


def test_add_gate(empty_hydro_system):
    gate = Gate("switch")
    empty_hydro_system.add_node(gate)
    assert empty_hydro_system.gates == [gate]
    assert empty_hydro_system.my_nodes == [gate]


def test_add_discharge(empty_hydro_system):
    res1 = Reservoir("res1", min_volume=0, max_volume=12)
    res2 = Reservoir("res2", min_volume=0, max_volume=12)

    dis = Discharge(res1, res2)
    empty_hydro_system.add_nodes_from([res1, res2])

    empty_hydro_system.add_edge(dis)
    assert empty_hydro_system.my_edges == [dis]
    assert empty_hydro_system.discharges == [dis]


def test_add_spillage(empty_hydro_system):
    res1 = Reservoir("res1", min_volume=0, max_volume=12)
    res2 = Reservoir("res2", min_volume=0, max_volume=12)

    spi = Spillage(res1, res2)
    empty_hydro_system.add_nodes_from([res1, res2])

    empty_hydro_system.add_edge(spi)
    assert empty_hydro_system.my_edges == [spi]
    assert empty_hydro_system.spillages == [spi]


def test_add_bypass(empty_hydro_system):
    res1 = Reservoir("res1", min_volume=0, max_volume=12)
    res2 = Reservoir("res2", min_volume=0, max_volume=12)

    byp = Bypass(res1, res2)
    empty_hydro_system.add_nodes_from([res1, res2])

    empty_hydro_system.add_edge(byp)
    assert empty_hydro_system.my_edges == [byp]
    assert empty_hydro_system.bypasses == [byp]
