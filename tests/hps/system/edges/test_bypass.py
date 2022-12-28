import pytest

import numpy as np

from hps.system.edges.bypass import Bypass
from hps.system.nodes import Reservoir


@pytest.fixture()
def bypass():
    parent = Reservoir("res1", 0, 20)
    child = Reservoir("res2", 0, 10)
    return Bypass(parent=parent, child=child)


def test_min_flow(bypass):
    assert bypass.min_flow == 0.0


def test_max_flow(bypass):
    assert bypass.max_flow == np.inf


def test_parent(bypass):
    assert isinstance(bypass.parent, Reservoir)


def test_child(bypass):
    assert isinstance(bypass.child, Reservoir)


def test_name(bypass):
    assert bypass.name == "res1 -> res2"
