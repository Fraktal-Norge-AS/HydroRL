#%%
from abc import ABCMeta, abstractmethod, abstractproperty
from operator import contains

from matplotlib.pyplot import legend
import logging
from typing import Dict, Optional

import pandas as pd
import numpy as np
import pytz

from hydro_systems import HSGen
from core.timeindex import CombinedTimeIndexer, ITimeIndexer, TimeIndexer
from server.model import Agent, Forecast, ReportDatum, SeriesLink, Upload, HydroSystem
from core.markov_chain import MarkovChain, Noise
from server.model import Forecast, SeriesLink, TimeDataValue, TimeDataSery


class IInflowPriceForecastData(metaclass=ABCMeta):
    @abstractproperty
    def hydro_system(self):
        pass

    @abstractproperty
    def inflow(self):
        pass

    @abstractproperty
    def price(self):
        pass


class InflowPriceForecastData(IInflowPriceForecastData):
    def __init__(self, hydro_system, inflow, price):
        self._hydro_system = hydro_system
        self._inflow = inflow
        self._price = price

    @property
    def hydro_system(self):
        return self._hydro_system

    @property
    def inflow(self):
        return self._inflow

    @property
    def price(self):
        return self._price


class IInflowPricesampler(metaclass=ABCMeta):
    @abstractmethod
    def sample_episode(self):
        pass

    @abstractmethod
    def reset_raw_episode_index(self, seed):
        pass


class InflowPriceSampler(IInflowPricesampler):
    def __init__(
        self,
        forecast_data: InflowPriceForecastData,
        time_indexer: ITimeIndexer,
        n_clusters=7,
        is_eval=False,
        sample_noise=Noise.Off,
        logger=None,
        seed=42,
    ):
        """
        Takes in inflow and price forecast, processes it to required time period and trains a forecast
        generator used for sampling episodes.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.forecast_data = forecast_data
        self.time_indexer = time_indexer
        self.n_clusters = n_clusters
        self.sampled_index = 0  # Counter for sampled episodes
        self.raw_index = 0  # Counter used for sampling raw episodes
        self.n_raw_episodes = len(forecast_data.inflow.columns)

        self.is_eval = is_eval  # Whether class is used in an evaluation environment

        self.df_i = InflowPriceSampler.mean_resample(self.time_indexer, forecast_data.inflow)
        self.df_p = InflowPriceSampler.mean_resample(self.time_indexer, forecast_data.price)

        n_nulls = self.df_p.isnull().sum().mean() or self.df_i.isnull().sum().mean()
        if n_nulls:
            self.logger.warning(
                "Using forward filling and then backwardfilling as some values in resampled forecast nan."
            )
            self.df_i = self.df_i.ffill().bfill()
            self.df_p = self.df_p.ffill().bfill()

        if not self.is_eval:
            data = np.moveaxis(np.stack((self.df_p.values, self.df_i.values)), source=0, destination=-1)
            self.forecast_generator = MarkovChain(
                data, n_clusters=self.n_clusters, seed=seed, sample_noise=sample_noise
            )

            # Inflow is double-sided clipped, energy price is one-sided clipped
            # Given no pumping, the actions would be the same whether the price is 0 or -10.
            # Inflow is double-sided clipped in order to not shift the mean.

            clusters = np.array([cluster.cluster_centers_ for cluster in self.forecast_generator.cls_])
            self.sample_min = np.zeros_like(clusters.min(axis=1))
            self.sample_max = clusters.max(axis=1) + clusters.min(axis=1)
            self.sample_max[:, 0] = np.inf  # No upper limit on price

    @staticmethod
    def mean_resample(time_indexer, df):
        df_resampled = pd.DataFrame(0.0, index=time_indexer.index, columns=df.columns)
        for i, (from_time, to_time) in enumerate(zip(time_indexer.index[:-1], time_indexer.index[1:])):
            df_resampled.iloc[i, :] = df[(df.index >= from_time) & (df.index < to_time)].mean().values

        df_resampled.iloc[-1] = df[(df.index >= to_time)].mean().values

        return df_resampled

    def _get_raw_episode(self):
        if self.raw_index >= self.n_raw_episodes:
            self.raw_index = 0

        price = self.df_p.iloc[:, self.raw_index].values
        inflow = self.df_i.iloc[:, self.raw_index].values

        episode_name = self.df_p.columns[self.raw_index]

        self.raw_index += 1

        return np.stack((price, inflow), axis=-1), episode_name

    def get_max_and_min_values(self):
        """
        Get the highest value of inflow and price for the sampling.
        Used for scaling purposes in the agent environment.
        """
        if self.forecast_generator.n_features != 2:
            raise NotImplementedError("Only implemented for n_features = 2")

        # Dim: time x clusters x features
        clusters = np.array([cluster.cluster_centers_ for cluster in self.forecast_generator.cls_])
        min_values = clusters.min(axis=1).min(axis=0)
        max_values = clusters.max(axis=1).max(axis=0)

        return min_values, max_values

    def get_max_and_min_values_forecast(self):
        return np.array([self.df_p.min().min(), self.df_i.min().min()]), np.array(
            [self.df_p.max().max(), self.df_i.max().max()]
        )

    def reset_raw_episode_index(self):
        self.raw_index = 0

    def sample_episode(self, initial_node: Optional[int] = None):
        """
        Sample inflow and price data for an episode.
        """
        if self.is_eval:
            episode, name = self._get_raw_episode()
        else:
            _, episode = self.forecast_generator.sample(initial_node=initial_node)
            name = self.sampled_index
            self.sampled_index += 1
            episode = np.clip(episode, self.sample_min, self.sample_max)

        return episode, name


def read_forecast_from_db(session, forecast_id: int, hydro_system: str, from_date, to_date):
    """
    Read the entire forecast from db.
    """
    hydro_system_id = session.query(Forecast).get(forecast_id).HydroSystemId
    hydro_system_db = session.query(HydroSystem).get(hydro_system_id).Name
    if hydro_system_db != hydro_system:
        raise ValueError(f"Forecast SystemId ({hydro_system_db}) does not match required hydro_system ({hydro_system})")

    # Ensure UTC before query db
    from_date = from_date.astimezone(pytz.utc)
    to_date = to_date.astimezone(pytz.utc) + pd.Timedelta("32D")

    series_links = session.query(SeriesLink).filter_by(ForecastId=forecast_id).all()
    forecast_dct = {}
    series_descriptions = {"Inflow": "InflowSeriesId", "Price": "PriceSeriesId"}
    for description in series_descriptions:
        df = None
        for s in series_links:

            time_data_series_id = getattr(s, series_descriptions[description])
            time_data_series = session.query(TimeDataSery).get(time_data_series_id)
            scen_year = time_data_series.Description
            sql = "SELECT TimeStampOffset, Value as '{}' from TimeDataValue where TimeDataSeriesId = {}".format(
                scen_year, time_data_series_id
            )

            series = pd.read_sql_query(sql, session.connection())
            series["TimeStampOffset"] = pd.to_datetime(series["TimeStampOffset"])
            series.set_index("TimeStampOffset", inplace=True)

            if df is None:
                df = series
            else:
                df = series.merge(df, left_index=True, right_index=True)
        forecast_dct[description] = df

    forecast_data = InflowPriceForecastData(hydro_system, forecast_dct["Inflow"], forecast_dct["Price"])

    return forecast_data


def get_start_end_time_forecast(session, forecast_id):
    time_data_series_id = session.query(SeriesLink).filter_by(ForecastId=forecast_id).first()
    time_data_series = session.query(TimeDataSery).get(time_data_series_id.InflowSeriesId)

    start = time_data_series.StartTime
    end = time_data_series.EndTime
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)

    return start, end
