import pytest
from hps.system.inflow import SimpleInflowModel


@pytest.fixture()
def simple_inflow():
    return SimpleInflowModel(mean_yearly_inflow=20, series_id=420)


def test_simple_inflow(simple_inflow):
    assert simple_inflow.mean_yearly_inflow == 20
    assert simple_inflow.series_id == 420
