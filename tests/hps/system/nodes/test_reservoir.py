import pytest
from hps.system.nodes.reservoir import Reservoir


@pytest.fixture()
def reservoir():
    return Reservoir("res1", min_volume=0, max_volume=12)


def test_min_volume(reservoir):
    assert reservoir.min_volume == 0
    with pytest.raises(ValueError):
        reservoir.min_volume = 13

def test_max_volum(reservoir):
    assert reservoir.max_volume == 12

def test_to_dict(reservoir):

    actual = reservoir.to_dict()
    expected = {
        'Reservoir':
            {'name': 'res1',
            'min_volume': 0,
            'max_volume': 12,
            'inflow_model': {'NullInflow': {}},
            'tank_water_cost': 1000000.0,
            'head': None,
            'energy_equivalent': None,
            'price_of_spillage': 1.0
        }
    }

    assert actual == expected