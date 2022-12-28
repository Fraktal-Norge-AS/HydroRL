from typing import Dict, List
from enum import Enum
import logging
from typing import Optional
from hps.rl.environment.hscomponents import HSystem
from hps.rl.settings import ObservationSettings
from core.value_scaler import LogScaler, NormalizeLogScaler, ConstantScaler
from core.timeindex import ITimeIndexer
import numpy as np
import pandas as pd

import gym


class ObservationsName(str, Enum):
    relative_volume = "relvol_"
    volume = "vol_"
    end_volume = "end_vol_"
    inflow = "inflow_"
    cycle = "cycle_"
    linear_time_up = "lin_time_up"
    linear_time_down = "ling_time_down"
    seasonal_linear_time = "seasonal_linear_time"
    seasonal_cosine_time = "seasonal_cosine_time"
    price = "price_"
    number_of_sectors = "num_sectors_"
    unique_step_size = "unique_step_size_"
    weekday = "weekday_"
    hour_bin = "hour_bin_"
    fourier_time = "fourier_time_"


class Observations(str, Enum):
    Time = "Time"


class LinearTimePeriod(str, Enum):
    Yearly = "Yearly"


class ObservationsGenerator:
    def __init__(
        self,
        observation_settings: ObservationSettings,
        time_indexer: ITimeIndexer,
        is_eval: bool,
        logger: Optional[logging.Logger] = None,
    ):

        self.is_eval = is_eval
        self.logger = logger or logging.getLogger(__name__)
        if observation_settings.log_normalize_price_scaler:
            self.price_scaler = NormalizeLogScaler(min_value=0.0, max_value=observation_settings.global_max_price)
        else:
            self.price_scaler = ConstantScaler(base_value=observation_settings.global_max_price)

        self.inflow_scaler = LogScaler(base_value=observation_settings.global_max_inflow)

        self.time_indexer = time_indexer
        self.acc_step_size_hours = np.append([0], np.cumsum(time_indexer.step_size_hours))
        self.scaled_time = self.acc_step_size_hours / self.time_indexer.sum_hours
        self.scaled_time_length = self.scaled_time[1] - self.scaled_time[0]
        self.unique_step_size_hours = np.unique(self.time_indexer.step_size_hours)
        if len(self.unique_step_size_hours) < 2:
            observation_settings.include_different_time_lengths = False

        self.weekday_encoding = pd.get_dummies(time_indexer.index.weekday)

        self.inflow_res = None
        self.observation_settings = observation_settings
        if observation_settings.num_trig > 0:
            trig_shifts = np.linspace(start=0, stop=1, num=observation_settings.num_trig, endpoint=False)
            self.cycles = self._init_cyclic(self.scaled_time, trig_shifts)

        self.seasonal_linear = [self.normalize_to_year(time_stamp) for time_stamp in self.time_indexer.index]
        self.seasonal_cosine = [np.cos(2 * np.pi * i) for i in self.seasonal_linear]

        if max(time_indexer.step_size_hours) < 24:
            self.hourly_cols, self.hourly_ohe = self._init_hourly_ohe(self.observation_settings.hourly_bin_interval)
        else:
            self.hourly_cols, self.hourly_ohe = [""], None
            if self.observation_settings.include_hourly_bins:
                self.observation_settings.include_hourly_bins = False
                self.logger.warning(
                    "'include_hourly_bins' set to 'False' as it does not make sense when time resolution is above 24 hours."
                )

        self.weekday_cols, self.weekday_ohe = self._init_weekday_ohe()

    def get_space(self, step, hydro_system, current_price, current_inflow):
        obs_dict = self.get_observations_dict(
            step=step, hydro_system=hydro_system, current_price=current_price, current_inflow=current_inflow
        )

        time_val = obs_dict.pop(ObservationsName.fourier_time)

        observation_space = gym.spaces.Dict(
            {
                "obs": gym.spaces.Box(-1, 1, shape=(len(obs_dict),), dtype=np.float64),  # NB
                ObservationsName.fourier_time: gym.spaces.Box(np.array([0]), np.array([np.inf]), dtype=np.float64),
            }
        )

        return observation_space

    @staticmethod
    def normalize_to_year(time_stamp):
        start = pd.Timestamp(year=time_stamp.year, month=1, day=1, hour=0, minute=0, tz=time_stamp.tz)
        end = pd.Timestamp(year=time_stamp.year + 1, month=1, day=1, hour=0, minute=0, tz=time_stamp.tz)
        seconds_in_year = (end - start).total_seconds()
        return (time_stamp - start).total_seconds() / seconds_in_year

    @staticmethod
    def _init_cyclic(scaled_values, trig_shifts):
        cycles = []
        for shift in trig_shifts:
            cycles.append(ObservationsGenerator._init_sin(scaled_values, shift))
            cycles.append(ObservationsGenerator._init_cos(scaled_values, shift))
        return cycles

    def _init_hourly_ohe(self, interval: int):
        if 24 % interval:
            self.logger.warning("Hourly bins interval are not evenly distributed.")

        hourly_bins = pd.interval_range(start=0, end=24, periods=int(24 / interval), closed="left")

        binned_values = pd.cut(self.time_indexer.index.hour, bins=hourly_bins)
        df_hour_ohe = pd.get_dummies(binned_values)
        return df_hour_ohe.columns.astype(str).to_list(), df_hour_ohe.values

    def _init_weekday_ohe(self) -> pd.DataFrame:
        df_weekday_ohe = pd.get_dummies(self.time_indexer.index.day_name())
        return df_weekday_ohe.columns.astype(str).to_list(), df_weekday_ohe.values

    @staticmethod
    def _init_cos(vals, phase_shift):
        return (np.cos(np.pi * (vals + phase_shift)) + 1) / 2.0

    @staticmethod
    def _init_sin(vals, phase_shift):
        return (np.sin(np.pi * (-1 / 2 + vals + phase_shift)) + 1) / 2.0

    def get_observations(self, step: int, hydro_system: HSystem, current_price: List, current_inflow: Dict):
        obs_dict = self.get_observations_dict(step, hydro_system, current_price, current_inflow)

        if self.observation_settings.time_periods:
            time_val = obs_dict.pop(ObservationsName.fourier_time)

            return {"obs": np.array(list(obs_dict.values()), dtype=np.float32), ObservationsName.fourier_time: time_val}
        else:
            return {"obs": np.array(list(obs_dict.values()), dtype=np.float32)}

    def get_observations_dict(self, step: int, hydro_system: HSystem, current_price: List, current_inflow: Dict):
        """
        Get the observations as a dictionary.

        Notice that the (time) step and the time state in the hydro system should be equal. I.e. that
        the current state of the hydro system is refering to the correct (time) step value. In general the
        hydro system state is s_{t+1}, such that the provided (time) state should also be t+1.

        :param step: The given step.
        :return: dictionary with names of observation as key.
        """

        settings = self.observation_settings
        if self.inflow_res is None:
            self.inflow_res = [r.name for r in hydro_system.reservoirs if r is not r.is_ocean][0]

        obs = {}
        if settings.include_hourly_bins:
            for i, col in enumerate(self.hourly_cols):
                obs[ObservationsName.hour_bin + col] = self.hourly_ohe[step, i]

        if settings.include_weekday_bins:
            for i, wday in enumerate(self.weekday_cols):
                obs[ObservationsName.weekday + wday] = self.weekday_ohe[step, i]

        for res in hydro_system.reservoirs:
            if not res.is_ocean:
                if settings.include_vol:
                    obs[ObservationsName.volume + res.name] = res.current_volume / hydro_system.maximum_volume
                    obs[ObservationsName.relative_volume + res.name] = res.current_volume / res.max_volume
                if settings.include_end_vol:
                    obs[ObservationsName.end_volume + res.name] = res.end_volume / hydro_system.maximum_volume

                if settings.include_flow:  # Add Inflow for each reservoir
                    value = self.inflow_scaler.scale(current_inflow[res.name][step], clip=True)
                    obs[ObservationsName.inflow + res.name] = value

        if settings.num_trig > 0:
            for i, fun in enumerate(self.cycles):
                obs[ObservationsName.cycle + str(i)] = fun[step]

        if settings.include_lin:
            obs[ObservationsName.linear_time_up] = self.scaled_time[step]
            obs[ObservationsName.linear_time_down] = 1 - self.scaled_time[step]

        if settings.time_periods:
            obs[ObservationsName.fourier_time] = self.acc_step_size_hours[step]

        if settings.include_seasonal_cosine_time:
            obs[ObservationsName.seasonal_cosine_time] = self.seasonal_cosine[step]

        if settings.include_seasonal_linear_time:
            obs[ObservationsName.seasonal_linear_time] = self.seasonal_linear[step]

        for delta_step in range(settings.price_steps):
            value = 0
            if step - delta_step > 0:
                value = 2 * (self.price_scaler.scale(current_price[step - delta_step], clip=True) - 0.5)
            else:
                value = 2 * (self.price_scaler.scale(current_price[step], clip=True) - 0.5)
            obs[ObservationsName.price + str(delta_step)] = value

        if settings.num_sectors is not None:
            sector = ObservationsGenerator.get_sector(settings.num_sectors, self.scaled_time[step])
            for i, val in enumerate(sector):
                obs[ObservationsName.number_of_sectors + str(i)] = val

        if settings.include_different_time_lengths:
            for unique_val in self.unique_step_size_hours:
                val = 0
                if unique_val == self.time_indexer.step_size_hours[step]:
                    val = 1
                obs[ObservationsName.unique_step_size + str(unique_val)] = val

        return obs

    @staticmethod
    def get_sector(sectors, value):
        num_sector = np.linspace(0, 1, num=sectors + 1)
        return np.where((value < num_sector[1:]) & (value >= num_sector[:-1]), 1, 0)
