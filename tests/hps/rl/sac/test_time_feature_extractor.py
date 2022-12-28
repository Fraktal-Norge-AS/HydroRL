import pytest
import pandas as pd
import numpy as np

from gym import spaces
from torch import nn
import torch as th
from stable_baselines3.common.utils import get_device

from hps.rl.environment.observations_generator import ObservationsGenerator, ObservationsName
from core.timeindex import FromPeriodTimeIndexer
from hps.rl.sac.time_feature_extractor import TimeFourierFeatureExtractor
from hps.rl.settings import ObservationSettings
from tests.hps.rl.environment.test_hscomponents import hydro_system


def test_time_fourier_feature_extractor(hydro_system):

    observations_settings = ObservationSettings()
    observations_settings.global_max_inflow = 10.
    observations_settings.global_max_price = 100.

    start = pd.Timestamp("2020-01-01T00:00:00Z")
    periods = 365
    freq = '1D'

    time_indexer = FromPeriodTimeIndexer(from_datetime=start, periods=periods, freq=freq)

    observation_generator = ObservationsGenerator(
        observation_settings=observations_settings,
        time_indexer=time_indexer,
        is_eval=False)

    step = 1
    current_price = np.array([10.]*periods, dtype=np.float64)
    current_inflow = {res.name: [1.0]*periods for res in hydro_system.reservoirs if not res.is_ocean}

    obs_dict = observation_generator.get_observations_dict(
            step=step,
            hydro_system=hydro_system,
            current_price=current_price,
            current_inflow=current_inflow)

    obs = np.array([0.0 for key, val in obs_dict.items() if key not in ObservationsName.fourier_time])
    obs_min = np.zeros_like(obs)
    obs_max = 10 * np.ones_like(obs)
    
    obs_dct = {
        "obs": th.tensor(obs, device=get_device()),
        ObservationsName.fourier_time: th.tensor(np.array([obs_dict[ObservationsName.fourier_time]]), device=get_device())
    }    

    observation_space = spaces.Dict({
        "obs": spaces.Box(obs_min, obs_max, dtype=np.float64),
        ObservationsName.fourier_time: spaces.Box(np.array([0]), np.array([np.inf]), dtype = np.float64)})

    for key, space in observation_space.spaces.items():
        print(key, space, space.shape)

    time_periods = [24, 24*7]

    feature_extractor = TimeFourierFeatureExtractor(
        observation_space=observation_space,
        time_periods=time_periods
    )

    val = feature_extractor(obs_dct)

    assert th.all(th.isclose(val, th.as_tensor([0.9159, -0.969,  0.0,  0.0,  0.0,  0.0,  0.0, 0.0], dtype=th.float64, device=get_device()), rtol=0.0001))
    feature_extractor.features_dim == 8
    list(feature_extractor.extractors.keys()) == [key for key in observation_space]
    

def test_cosine_periods():

    time_periods = np.array([24, 24*7])[:,np.newaxis]

    T = 8760
    x = np.arange(0, T + 1)

    vals = np.cos(2*np.pi*time_periods/T*x)
    act = vals[:,:2]

    des = np.array([
        [1.        , 0.99985184],
        [1.        , 0.99274872]])

    np.testing.assert_almost_equal(actual=act, desired=des)