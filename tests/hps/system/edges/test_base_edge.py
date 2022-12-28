import pytest

from hps.system.edges.spillage import BaseHydroEdge
from hps.system.nodes import Reservoir


@pytest.fixture()
def base_edge():
    parent = Reservoir("res1", 0, 20)
    child = Reservoir("res2", 0, 10)
    return BaseHydroEdge(parent=parent, child=child, min_flow=0, max_flow=10)


def test_parent(base_edge):
    assert isinstance(base_edge.parent, Reservoir)


def test_child(base_edge):
    assert isinstance(base_edge.child, Reservoir)


def test_child_is_parent():
    with pytest.raises(ValueError):
        parent = Reservoir("res", 0, 20)
        BaseHydroEdge(parent=parent, child=parent, min_flow=0, max_flow=10)


def test_name(base_edge):
    assert base_edge.name == "res1 -> res2"
