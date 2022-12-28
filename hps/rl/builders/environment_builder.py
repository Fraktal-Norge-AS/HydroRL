from server.model import Reservoir
import pandas as pd
import pytz

from hps.rl.settings import RunSettings
from hps.rl.environment.hsenvironment import HSEnvironment

from hydro_systems import HSGen

from sqlalchemy.orm import sessionmaker
from server.appsettings import appSettings
from hps.exogenous.inflow_and_price import get_start_end_time_forecast, read_forecast_from_db, InflowPriceSampler
from core.timeindex import MultipleCombinedTimeIndexer, ITimeIndexer, TimeIndexer
from hps.rl.settings import ObservationSettings
from hps.rl.environment.observations_generator import ObservationsGenerator


local_tz = pytz.timezone("Europe/Oslo")


class EnvironmentBuilder:
    def __init__(self, run_settings: RunSettings, forecast_id):
        self.run_settings = run_settings
        self.forecast_id = forecast_id

    def build_time_indexers(self, session):
        forecast_start, forecast_end = get_start_end_time_forecast(session, self.forecast_id)

        # Train time indexer
        if isinstance(self.run_settings.train_intervals, list) and isinstance(
            self.run_settings.train_step_frequency, list
        ):
            train_time_indexer = MultipleCombinedTimeIndexer(
                from_datetime=forecast_start,
                periods=self.run_settings.train_intervals,
                freqs=self.run_settings.eval_step_frequency,
            )
        else:
            train_time_indexer = TimeIndexer(
                pd.date_range(
                    start=forecast_start,
                    periods=self.run_settings.train_intervals + 1,  # Last index is end of episode
                    freq=self.run_settings.train_step_frequency,
                )
            )

        # Eval time indexer
        if isinstance(self.run_settings.eval_intervals, list) and isinstance(
            self.run_settings.eval_step_frequency, list
        ):
            eval_time_indexer = MultipleCombinedTimeIndexer(
                from_datetime=forecast_start,
                periods=self.run_settings.eval_intervals,
                freqs=self.run_settings.eval_step_frequency,
            )
        else:
            eval_time_indexer = TimeIndexer(
                pd.date_range(
                    start=forecast_start,
                    periods=self.run_settings.eval_intervals + 1,  # Last index is end of episode
                    freq=self.run_settings.eval_step_frequency,
                )
            )

        if train_time_indexer.to_datetime > forecast_end or eval_time_indexer.to_datetime > forecast_end:
            raise ValueError("Forecasts ends before required end time of episode.")

        return train_time_indexer, eval_time_indexer

    def build_samplers(self, session, train_time_indexer: ITimeIndexer, eval_time_indexer: ITimeIndexer):
        price_inflow_data = read_forecast_from_db(
            session,
            self.forecast_id,
            hydro_system=self.run_settings.system,
            from_date=train_time_indexer.from_datetime,
            to_date=train_time_indexer.to_datetime,
        )

        train_inflow_price_sampler = InflowPriceSampler(
            price_inflow_data,
            train_time_indexer,
            is_eval=False,
            seed=self.run_settings.forecast_sampling_seed,
            n_clusters=self.run_settings.n_clusters,
            sample_noise=self.run_settings.sample_with_noise,
        )

        eval_inflow_price_sampler = InflowPriceSampler(
            price_inflow_data,
            eval_time_indexer,
            is_eval=True,
            seed=self.run_settings.forecast_sampling_seed,
            n_clusters=None,
        )

        return train_inflow_price_sampler, eval_inflow_price_sampler

    def build_observations_generator(
        self, observation_settings: ObservationSettings, time_indexer: ITimeIndexer, is_eval: bool
    ):
        return ObservationsGenerator(observation_settings, time_indexer, is_eval)

    def build_env(
        self,
        name,
        hs_env,
        time_indexer,
        inflow_price_sampler,
        observations_generator,
        reward_scaler,
        discounter,
        price_scaler,
        is_eval,
        randomize_init_vol,
        initial_collect_episodes,
    ):
        return HSEnvironment(
            name,
            hs_env,
            time_indexer=time_indexer,
            inflow_price_sampler=inflow_price_sampler,
            observations_generator=observations_generator,
            reward_scaler=reward_scaler,
            discounter=discounter,
            price_scaler=price_scaler,
            is_eval=is_eval,
            randomize_init_vol=randomize_init_vol,
            initial_collect_episodes=initial_collect_episodes,
        )

    def build_hs(self, session, project_run_id):

        start_volume = self.get_start_volume(session, project_run_id)

        return HSGen.create_system(
            name=self.run_settings.system,
            start_volume=start_volume,
            price_of_spillage=self.run_settings.price_of_spillage,
            use_linear_model=self.run_settings.use_linear_model,
        )

    def get_start_volume(self, session, project_run_id):
        from server.model import ProjectRunStartVolume, Reservoir

        start_volume = {}

        project_start_volumes = (
            session.query(ProjectRunStartVolume, Reservoir)
            .join(Reservoir, Reservoir.ReservoirId == ProjectRunStartVolume.ReservoirId)
            .filter(ProjectRunStartVolume.ProjectRunId == project_run_id)
            .all()
        )

        for proj_run, res in project_start_volumes:
            start_volume[res.Name] = proj_run.Value

        return start_volume
