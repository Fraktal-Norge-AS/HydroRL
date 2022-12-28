from tests.hps.rl.test_timeindex import time_indexer
from numpy.testing._private.utils import assert_almost_equal, assert_array_almost_equal
import pytest
from pathlib import Path

import pandas as pd

from hps.exogenous.inflow_and_price import InflowPriceSampler, InflowPriceForecastData
from core.timeindex import TimeIndexer


@pytest.fixture()
def forecast_data():
    hydro_system = "Sys"
    path=Path(__file__).resolve().parent
    df_inflow = pd.read_csv(path/Path("data/inflow.csv"), index_col=0, parse_dates=["date"])
    df_price = pd.read_csv(path/Path("data/price.csv"), index_col=0, parse_dates=["date"])
    return InflowPriceForecastData(hydro_system, inflow=df_inflow, price=df_price)
     

@pytest.fixture()
def inflow_price_sampler(forecast_data):
   
    steps = 12 + 1 # Last index is end of episode
    freq = '1M'
    n_clusters=7
    
    time_index = pd.date_range(
        start=forecast_data.inflow.index[0],
        periods=steps,
        freq=freq)
    time_indexer = TimeIndexer(time_index)

    return InflowPriceSampler(
        forecast_data=forecast_data, time_indexer=time_indexer,
        n_clusters=n_clusters
    )

@pytest.mark.skip(reason="Slow test")
def test_inflow_price_sampler_resampling(forecast_data):
    steps = [3600, 365, 52, 12]
    freqs = ['3H', '1D', '1W', '1M']
    for step, freq in zip(steps, freqs):
        time_index = pd.date_range(
        start=forecast_data.inflow.index[0],
        periods=step,
        freq=freq)
        time_indexer = TimeIndexer(time_index)
        ip_sampler = InflowPriceSampler(forecast_data=forecast_data, time_indexer=time_indexer, n_clusters=1)

        assert len(ip_sampler.df_i) == step
        assert ip_sampler.df_p.index[0] == time_index[0]


def test_properties(inflow_price_sampler):    
    assert_almost_equal(inflow_price_sampler.n_raw_episodes, 30)


def test_episode_sampling_size(inflow_price_sampler):
    episode, _ = inflow_price_sampler.sample_episode()

    assert episode.shape == (13, 2)


def test_episode_sampling(inflow_price_sampler):
    ep1, name1 = inflow_price_sampler.sample_episode()
    ep2, name2 = inflow_price_sampler.sample_episode()
    
    assert name1 == 0
    assert name2 == 1
    
    assert ep1.shape == (13, 2)
    assert ep2.shape == (13, 2)


@pytest.fixture()
def inflow_price_sampler_eval(forecast_data):

    steps=12 + 1
    freq = '1M'
    n_clusters=7
    
    time_index = pd.date_range(
        start=forecast_data.inflow.index[0],
        periods=steps,
        freq=freq)
    time_indexer = TimeIndexer(time_index)

    return InflowPriceSampler(
        forecast_data=forecast_data, time_indexer=time_indexer,
        n_clusters=n_clusters, is_eval=True
    )


def test_episode_sampling_eval(inflow_price_sampler_eval):
    ep1, name1 = inflow_price_sampler_eval.sample_episode()
    ep2, name2 = inflow_price_sampler_eval.sample_episode()
    inflow_price_sampler_eval.raw_index = inflow_price_sampler_eval.n_raw_episodes
    _, namen = inflow_price_sampler_eval.sample_episode()

    assert name1 == inflow_price_sampler_eval.df_p.columns[0]
    assert name2 == inflow_price_sampler_eval.df_p.columns[1]
    assert namen == inflow_price_sampler_eval.df_p.columns[0]

    assert ep1.shape == (13, 2)
    assert ep2.shape == (13, 2)

    assert_array_almost_equal(ep1[:,0], inflow_price_sampler_eval.df_p.iloc[:,0].values)
    assert_array_almost_equal(ep1[:,1], inflow_price_sampler_eval.df_i.iloc[:,0].values)

    assert_array_almost_equal(ep2[:,0], inflow_price_sampler_eval.df_p.iloc[:,1].values)
    assert_array_almost_equal(ep2[:,1], inflow_price_sampler_eval.df_i.iloc[:,1].values)

