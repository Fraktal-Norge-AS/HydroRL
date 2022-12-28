from hps.rl.logging.tensorboard_logger import TensorboardTrainLogger
from hps.rl.environment.end_value_calculation import (
    IEndValueCalculation,
    ProvidedPriceEndValueCalculation,
    QEndValueCalculation,
    EndStateIncentive,
    PriceEndValueCalculation,
    EmptyEndValueCalculation,
)
from hps.rl.builders.agent_builder import AgentBuilder
from hps.rl.builders.environment_builder import EnvironmentBuilder
from hps.rl.logging.agent_plugin import AgentPlugin
from hps.rl.agent_runner import AgentRunner
from hps.rl.settings import RunSettingsSerializer

import numpy as np
import tensorflow as tf
import random as rand

from server.db_connection import create_engine
from sqlalchemy.orm import sessionmaker
from server.model import ProjectRun

from core.value_scaler import Discounter, PriceScaler, RewardScaler
import os


class RlBuilder:
    def __init__(self, run_settings, agent_settings, project_run):
        self.run_settings = run_settings
        self.agent_settings = agent_settings
        self.project_run = project_run
        self.project_run_id = project_run.ProjectRunId
        self.ensure_determinism = run_settings.ensure_determinism

    def random_init(self, seed):
        np.random.seed(seed)
        tf.random.set_seed(seed)
        rand.seed(seed)
        tf.compat.v1.random.set_random_seed(seed)

        if self.ensure_determinism:
            os.environ["PYTHONHASHSEED"] = str(seed)
            os.environ["TF_CUDNN_DETERMINISTIC"] = "1"
            tf.config.threading.set_inter_op_parallelism_threads(1)
            tf.config.threading.set_intra_op_parallelism_threads(1)

    @staticmethod
    def create_session():
        engine = create_engine()
        Session = sessionmaker(bind=engine)
        return Session()

    def build(self, plugin: AgentPlugin, train_plugin: TensorboardTrainLogger = None):
        self.random_init(self.agent_settings.seed)

        session = RlBuilder.create_session()

        env_builder = EnvironmentBuilder(self.run_settings, self.project_run.ForecastId)
        train_time_indexer, eval_time_indexer = env_builder.build_time_indexers(session)
        train_inflow_price_sampler, eval_inflow_price_sampler = env_builder.build_samplers(
            session, train_time_indexer, eval_time_indexer
        )

        train_hydro_system = env_builder.build_hs(session, self.project_run_id)
        eval_hydro_system = env_builder.build_hs(session, self.project_run_id)

        maximum_production = train_hydro_system.maximum_production
        num_steps = train_time_indexer.length
        average_step_size_hours = train_time_indexer.sum_hours / num_steps
        reward_scaler = RewardScaler(
            maximum_production=maximum_production,
            num_steps=num_steps,
            average_step_size_hours=average_step_size_hours,
            constant=self.run_settings.reward_scale_factor,
        )

        train_discounter = Discounter(discount_rate=self.run_settings.discount_rate, time_indexer=train_time_indexer)
        eval_discounter = Discounter(discount_rate=self.run_settings.discount_rate, time_indexer=eval_time_indexer)

        _, max_vals = train_inflow_price_sampler.get_max_and_min_values_forecast()
        self.run_settings.observation_settings.global_max_price = max_vals[0]
        self.run_settings.observation_settings.global_max_inflow = max_vals[1]
        train_price_scaler = PriceScaler(
            max_value=max_vals[0], min_value=0, scale_by=self.run_settings.price_scale_factor
        )
        eval_price_scaler = PriceScaler(
            max_value=max_vals[0], min_value=0, scale_by=self.run_settings.price_scale_factor
        )

        train_observation_generator = env_builder.build_observations_generator(
            self.run_settings.observation_settings, train_time_indexer, False
        )
        eval_observation_generator = env_builder.build_observations_generator(
            self.run_settings.observation_settings, eval_time_indexer, True
        )

        internal_train_env = env_builder.build_env(
            name="train",
            hs_env=train_hydro_system,
            time_indexer=train_time_indexer,
            inflow_price_sampler=train_inflow_price_sampler,
            observations_generator=train_observation_generator,
            reward_scaler=reward_scaler,
            discounter=train_discounter,
            price_scaler=train_price_scaler,
            is_eval=False,
            randomize_init_vol=self.run_settings.randomize_init_vol,
            initial_collect_episodes=self.agent_settings.episodes_to_initially_collect,
        )

        internal_eval_env = env_builder.build_env(
            name="evaluate",
            hs_env=eval_hydro_system,
            time_indexer=eval_time_indexer,
            inflow_price_sampler=eval_inflow_price_sampler,
            observations_generator=eval_observation_generator,
            reward_scaler=reward_scaler,
            discounter=eval_discounter,
            price_scaler=train_price_scaler,
            is_eval=True,
            randomize_init_vol=self.run_settings.randomize_init_vol,
            initial_collect_episodes=self.agent_settings.episodes_to_initially_collect,
        )

        sac_params = self.run_settings.sac_settings

        agent_builder = AgentBuilder(
            self.run_settings.agent_algorithm,
            sac_params,
            internal_train_env,
            train_observation_generator,
            initial_steps_to_collect=self.agent_settings.episodes_to_initially_collect
            * self.run_settings.train_intervals,
        )

        num_actions = internal_train_env.hydro_system.get_num_actions()

        agent = agent_builder.build(
            num_actions, self.agent_settings.output_checkpoint_folder, self.agent_settings.start_checkpoint_folder
        )
        agent_q = None
        # if self.agent_settings.q_value_checkpoint_folder:
        #     agent_q = agent_builder.build(self.agent_settings.q_value_checkpoint_folder)

        self.init_end_value_calculation(
            session,
            internal_train_env,
            internal_eval_env,
            maximum_production,
            self.run_settings.end_energy_price,
            agent_q,
        )

        return AgentRunner(self.run_settings, self.agent_settings, agent, internal_train_env, internal_eval_env, plugin)

    def init_end_value_calculation(
        self, session, internal_train_env, internal_eval_env, maximum_production, end_energy_price, tf_agent_q
    ):
        """
        Initialize the end value calculation.
        """

        train_end_value_calculation: IEndValueCalculation = EmptyEndValueCalculation()
        eval_end_value_calculation: IEndValueCalculation = EmptyEndValueCalculation()

        if self.run_settings.end_state_incentive in [
            EndStateIncentive.LastEnergyPrice,
            EndStateIncentive.MeanEnergyPrice,
        ]:
            train_end_value_calculation = PriceEndValueCalculation(
                end_type=self.run_settings.end_state_incentive, reservoirs=internal_train_env.hydro_system.reservoirs
            )

            eval_end_value_calculation = PriceEndValueCalculation(
                end_type=self.run_settings.end_state_incentive, reservoirs=internal_eval_env.hydro_system.reservoirs
            )

        elif self.run_settings.end_state_incentive == EndStateIncentive.ProvidedEndEnergyPrice:
            train_end_value_calculation = ProvidedPriceEndValueCalculation(
                reservoirs=internal_train_env.hydro_system.reservoirs, price=end_energy_price
            )

            eval_end_value_calculation = ProvidedPriceEndValueCalculation(
                reservoirs=internal_eval_env.hydro_system.reservoirs, price=end_energy_price
            )

        elif self.run_settings.end_state_incentive == EndStateIncentive.QValue:
            raise NotImplementedError("")

            if tf_agent_q is None:
                raise ValueError("'q_value_checkpoint_folder' missing from 'agent_settings'.")

            # Read Q run settings
            project_run_q = (
                session.query(ProjectRun)
                .filter(ProjectRun.ProjectRunId == self.project_run.PreviousQValueProjectRunId)
                .first()
            )
            q_settings = RunSettingsSerializer.deserialze(project_run_q.Settings)

            past_train_time_indexer, past_eval_time_indexer = EnvironmentBuilder(
                q_settings, project_run_q.ForecastId
            ).build_time_indexers(session)

            train_end_value_calculation = QEndValueCalculation(
                past_observations_settings=q_settings.observation_settings,
                current_time_indexer=internal_train_env.time_indexer,
                past_time_indexer=past_train_time_indexer,
                tf_agent=tf_agent_q,
                maximum_production=maximum_production,
                past_reward_scale_factor=q_settings.reward_scale_factor,
            )
            eval_end_value_calculation = QEndValueCalculation(
                past_observations_settings=q_settings.observation_settings,
                current_time_indexer=internal_train_env.time_indexer,
                past_time_indexer=past_eval_time_indexer,
                tf_agent=tf_agent_q,
                maximum_production=maximum_production,
                past_reward_scale_factor=q_settings.reward_scale_factor,
            )

        elif self.run_settings.end_state_incentive == EndStateIncentive.Off:
            pass
        else:
            raise NotImplementedError(
                "End state incentive '{}' not implemented.".format(self.run_settings.end_state_incentive)
            )

        internal_train_env.end_value_calculation = train_end_value_calculation
        internal_eval_env.end_value_calculation = eval_end_value_calculation
