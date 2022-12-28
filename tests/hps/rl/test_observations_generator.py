import pytest

import pandas as pd
import numpy as np

from hps.rl.environment.observations_generator import ObservationsGenerator
from hps.rl.settings import ObservationSettings
from core.timeindex import TimeIndexer


@pytest.fixture()
def obs_generator():
    observation_settings = ObservationSettings()

    time_indexer = TimeIndexer(pd.date_range(
        start = pd.Timestamp("2020-01-01T00:00:00Z"),
        periods = 11, 
        freq='1D'
    ))
    
    return ObservationsGenerator(
        observation_settings=observation_settings,
        time_indexer=time_indexer,
        is_eval=False
    )

def test_observation_generator_constructor(obs_generator):
    actual = obs_generator.scaled_time
    exp = np.linspace(0,1,11)
    np.testing.assert_almost_equal(actual, exp)
    

def test_init_cyclic():
    trig_shifts = np.linspace(0,1,3, endpoint=False)
    scaled_vals = np.linspace(0,1,10, endpoint=False)

    actual_cyclic = np.array(ObservationsGenerator._init_cyclic(scaled_vals, trig_shifts))
    expected_cyclic = np.array([
        [0.        , 0.02447174, 0.0954915 , 0.20610737, 0.3454915 , 0.5       , 0.6545085 , 0.79389263, 0.9045085 , 0.97552826],
        [1.        , 0.97552826, 0.9045085 , 0.79389263, 0.6545085 , 0.5       , 0.3454915 , 0.20610737, 0.0954915 , 0.02447174],
        [0.25      , 0.39604415, 0.55226423, 0.70336832, 0.8345653 , 0.9330127 , 0.9890738 , 0.99726095, 0.95677273, 0.87157241],
        [0.75      , 0.60395585, 0.44773577, 0.29663168, 0.1654347 , 0.0669873 , 0.0109262 , 0.00273905, 0.04322727, 0.12842759],
        [0.75      , 0.87157241, 0.95677273, 0.99726095, 0.9890738 , 0.9330127 , 0.8345653 , 0.70336832, 0.55226423, 0.39604415],
        [0.25      , 0.12842759, 0.04322727, 0.00273905, 0.0109262 , 0.0669873 , 0.1654347 , 0.29663168, 0.44773577, 0.60395585]])

    np.testing.assert_almost_equal(actual_cyclic, expected_cyclic)


def test_num_sectors():
    actual = []
    for i in np.linspace(0, 1, num=5, endpoint=False):
        val = ObservationsGenerator.get_sector(sectors=5, value=i)
        actual.append(val)

    actual = np.array(actual)

    exp = np.eye(5)

    np.testing.assert_almost_equal(actual, exp)


#%%