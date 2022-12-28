import pytest

import numpy as np

from hps.system.edges.discharge import Discharge
from hps.system.nodes import Reservoir


@pytest.fixture()
def discharge():
    parent = Reservoir("res1", 0, 20)
    child = Reservoir("res2", 0, 10)
    return Discharge(parent=parent, child=child)


def test_min_flow(discharge):
    assert discharge.min_flow == 0.0


def test_max_flow(discharge):
    assert discharge.max_flow == np.inf


def test_parent(discharge):
    assert isinstance(discharge.parent, Reservoir)


def test_child(discharge):
    assert isinstance(discharge.child, Reservoir)


def test_name(discharge):
    assert discharge.name == "res1 -> res2"
