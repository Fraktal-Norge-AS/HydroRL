import pytest
from unittest.mock import Mock

from hps.system.nodes.creek import Creek
from hps.system.inflow import NullInflow, IInflow


@pytest.fixture()
def creek():
    return Creek(name="creek1")


def test_is_nullinflow(creek):
    assert isinstance(creek.inflow_model, NullInflow)


def test_add_inflow(creek):

    inflow = Mock(IInflow)
    creek.inflow_model = inflow
    assert isinstance(creek.inflow_model, IInflow)
