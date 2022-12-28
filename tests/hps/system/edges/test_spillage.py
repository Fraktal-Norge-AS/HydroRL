import pytest

import numpy as np

from hps.system.edges.spillage import Spillage
from hps.system.nodes import Reservoir


@pytest.fixture()
def spillage():
    parent = Reservoir("res1", 0, 20)
    child = Reservoir("res2", 0, 10)
    return Spillage(parent=parent, child=child)


def test_min_flow(spillage):
    assert spillage.min_flow == 0.0


def test_max_flow(spillage):
    assert spillage.max_flow == np.inf


def test_parent(spillage):
    assert isinstance(spillage.parent, Reservoir)


def test_child(spillage):
    assert isinstance(spillage.child, Reservoir)


def test_name(spillage):
    assert spillage.name == "res1 -> res2"
