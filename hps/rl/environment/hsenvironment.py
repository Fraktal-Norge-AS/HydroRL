import numpy as np
from gym import spaces, Env

from hps.exogenous.inflow_and_price import InflowPriceSampler
from hps.rl.environment.end_value_type import EndStateIncentive
from hps.rl.logging.report_name import ReportName
from hps.system.inflow import ScaleInflowModel, ScaleYearlyInflowModel
from hps.exogenous.inflow_and_price import InflowPriceSampler
from hps.rl.environment.hscomponents import HSystem
from hps.rl.settings import ObservationSettings
from hps.rl.environment.observations_generator import ObservationsGenerator, ObservationsName
from hps.rl.environment.end_value_calculation import EmptyEndValueCalculation, ProvidedPriceEndValueCalculation
from core.timeindex import ITimeIndexer
from core.data_structures import MyDataFrame
from hps.custom_box import CustomBox


class HSEnvironment(Env):
    def __init__(
        self,
        name: str,
        hydro_system: HSystem,
        time_indexer: ITimeIndexer,
        inflow_price_sampler: InflowPriceSampler,
        observations_generator: ObservationsGenerator,
        reward_scaler,
        discounter,
        price_scaler,
        initial_collect_episodes,
        is_eval=False,
        agent=None,
        randomize_init_vol=False,
        random_vol=False,
    ):
        self.name = name
        self.hydro_system = hydro_system
        self.inflow_price_sampler = inflow_price_sampler
        self.is_eval = is_eval
        self.agent = agent
        self.observations_generator = observations_generator
        self.time_indexer = time_indexer
        self.randomize_init_vol = randomize_init_vol
        self.end_value_calculation = EmptyEndValueCalculation()
        self.random_vol = random_vol
        # Scale the inflow to the system to the different reservoirs
        average_forecast_inflow = self.inflow_price_sampler.forecast_data.inflow.mean().mean()
        self.reservoir_scaling = self.get_reservoir_inflow_scaling(hydro_system, average_forecast_inflow)

        self.potential_function = ProvidedPriceEndValueCalculation(self.hydro_system.reservoirs, 0)

        # Scaler used for the reward signals
        self.reward_scaler = reward_scaler
        self.discounter = discounter
        self.price_scaler = price_scaler

        self.current_inflow, self.current_price, self.forecast_name = self.get_forecast()

        if self.is_eval:
            reward_cols = [a.get_name() for a in self.hydro_system.sorted_actions] + ["sum"]
            self.reward = MyDataFrame(columns=reward_cols, n_elements=self.time_indexer.length, dtype=np.float32)

            self.report_df = None

            observation_cols = list(self.get_observations_dict(0).keys())
            self.gradient_df = MyDataFrame(
                columns=observation_cols, n_elements=self.time_indexer.length, dtype=np.float32
            )

        self.episode_ended = False
        self.current_step = 0
        self.action_space = self.action_spec()
        self.observation_space = self.observation_spec()

        self.current_episode = 0
        self.num_warmup_episodes = initial_collect_episodes

    @staticmethod
    def get_reservoir_inflow_scaling(hydro_system, average_forecast_inflow):
        res_scaling = {}
        for r in hydro_system.reservoirs:
            if not r.is_ocean:
                if isinstance(r.inflow_model, ScaleYearlyInflowModel):
                    res_scaling[r.name] = r.inflow_model.mean_inflow / average_forecast_inflow
                elif isinstance(r.inflow_model, ScaleInflowModel):
                    res_scaling[r.name] = r.inflow_model.scale_factor
        return res_scaling

    def reset_raw_episode_seed(self):
        self.inflow_price_sampler.reset_raw_episode_index()

    def get_forecast(self):
        """
        Inflow is a dict with the name of the reservoir as key and values are a list of inflows for each step.
        Price is a dict with the name of the price aree as key and values are a list of prices for each step.

        :param reservoir_scaling_dct: Dictionary with reservoir names as key and scaling factor as value
        :return: inflow_dct, price_dct
        """

        episode_vals, episode_name = self.inflow_price_sampler.sample_episode()

        inflow_dct = {}
        for res in self.reservoir_scaling:
            inflow_dct[res] = self.reservoir_scaling[res] * episode_vals[:, 1]

        price = episode_vals[:, 0]
        self.mean_price = np.mean(price)

        return inflow_dct, price, episode_name

    def action_spec(self):
        # return spaces.Box(low=0., high=1., shape=[self.hydro_system.get_num_actions()], dtype=np.float32)
        # return CustomSimpleBox(
        #     low=0., high=1., shape=[self.hydro_system.get_num_actions()], dtype=np.float32,
        #     activation_chance=0.10
        # )
        return CustomBox(
            low=0.0,
            high=1.0,
            environment=self,
            is_eval=self.is_eval,
            shape=[self.hydro_system.get_num_actions()],
            dtype=np.float32,
        )

    def observation_spec(self):
        if self.observations_generator.observation_settings.time_periods:
            obs_dict = self.get_observations(step=0)
            return spaces.Dict(
                {
                    "obs": spaces.Box(low=0.0, high=1.0, shape=obs_dict["obs"].shape),
                    ObservationsName.fourier_time: spaces.Box(low=0.0, high=np.Inf, shape=(1,)),
                }
            )
        else:
            obs_dict = self.get_observations(step=0)
            return spaces.Dict({"obs": spaces.Box(low=0.0, high=1.0, shape=obs_dict["obs"].shape)})

    def reset(self):
        self.episode_ended = False
        self.hydro_system.reset()
        self.current_step = 0
        self.q_value = 0.0
        self.end_reward = 0.0

        if not self.is_eval:
            if self.randomize_init_vol:
                for r in self.hydro_system.reservoirs:
                    if not r.is_ocean:
                        r.init_volume = np.random.random() * r.max_volume

        self.current_inflow, self.current_price, self.forecast_name = self.get_forecast()
        self.current_episode += 1
        if self.current_episode < self.num_warmup_episodes:
            self.action_space.new_episode(self.current_price)
        return self.get_observations(self.current_step)

    def step(self, norm_action):
        """Perform a step in the environment.

        :return: a TimeStep tuple of (step_type, reward, discount, new_observation)
        """
        if self.episode_ended:
            return self.reset()

        reward, finished, obs = self.__step(norm_action)

        if finished:
            self.episode_ended = True
        return obs, reward, self.episode_ended, {}

    def get_observations_dict(self, step):
        return self.observations_generator.get_observations_dict(
            step, self.hydro_system, self.current_price, self.current_inflow
        )

    def get_observations(self, step):
        return self.observations_generator.get_observations(
            step, self.hydro_system, self.current_price, self.current_inflow
        )

    def __step(self, in_norm_action: np.ndarray):
        """
        Perform a step with the given normalized action.

        Returns a tuple containing the scaled reward, whether the step was a final step, and the next state.

        The reward is given by the reward for the transition (s_t, a_t) -> s_{t+1}.
        The returned state is the state in the next step s_{t+1}.

        :param norm_action: Normalized action
        :returns: Tuple[pd.Series, reward, done]
        """

        if self.current_episode < self.num_warmup_episodes:
            if not self.is_eval:
                for r in self.hydro_system.reservoirs:
                    if not r.is_ocean:
                        r.init_volume = np.random.random() * r.max_volume

            self.action_space.set_step(self.current_step, self.get_observations_dict(self.current_step))

        is_final_time_step = self.current_step + 1 >= self.time_indexer.length
        price = self.current_price[self.current_step]
        scaled_price = self.price_scaler.scale(price)
        step_size = self.time_indexer.step_size_hours[self.current_step]

        inflows = {}
        for res in self.current_inflow:
            inflows[res] = self.current_inflow[res][self.current_step]

        potential_0 = self.potential_function.calculate()

        reward = self.hydro_system.execute(in_norm_action, step_size, scaled_price, inflows)

        potential_1 = self.potential_function.calculate()
        reward += potential_1 - potential_0

        if self.is_eval:
            for action in self.hydro_system.sorted_actions:
                value = action.get_value()
                name = action.get_name()
                self.reward[name][self.current_step] = value

        if is_final_time_step:
            if self.end_value_calculation.end_type == EndStateIncentive.QValue:
                self.end_reward = self.end_value_calculation.calculate(
                    self.hydro_system, self.current_price, self.current_inflow, in_norm_action
                )
            elif self.end_value_calculation.end_type == EndStateIncentive.MeanEnergyPrice:
                self.end_reward = self.end_value_calculation.calculate(self.price_scaler.scale(self.mean_price))
            elif self.end_value_calculation.end_type == EndStateIncentive.LastEnergyPrice:
                self.end_reward = self.end_value_calculation.calculate(scaled_price)
            elif self.end_value_calculation.end_type == EndStateIncentive.ProvidedEndEnergyPrice:
                self.end_reward = self.end_value_calculation.calculate()
            elif self.end_value_calculation.end_type == EndStateIncentive.Off:
                self.end_reward = 0.0
            else:
                raise NotImplementedError(f"EndStateIncentive {self.end_value_calculation.end_type} not implemented.")

            reward += self.end_reward

        reward = self.discounter.get_gamma(self.current_step) * reward
        scaled_reward = self.reward_scaler.scale(reward) * 100

        if self.is_eval:
            self.reward["sum"][self.current_step] = scaled_reward
            self.eval_report(scaled_price, price, in_norm_action, inflows)

        self.current_step += 1
        return scaled_reward, is_final_time_step, self.get_observations(self.current_step)

    def init_eval_report(self, actions, inflows):
        state = self.hydro_system.report_state(actions)

        report_cols = []
        for name, _ in state.items():
            report_cols.append(name)

        for key, _ in inflows.items():
            report_cols.append(ReportName.inflow + key)

        report_cols.append(ReportName.sum_money)
        report_cols.append(ReportName.sum_mwh)
        report_cols.append(ReportName.energy_price)
        report_cols.append(ReportName.scaled_energy_price)
        report_cols.append(ReportName.end_value + "_" + self.end_value_calculation.end_type)

        self.report_df = MyDataFrame(columns=report_cols, n_elements=self.time_indexer.length, dtype=np.float32)

    def get_energy_equivalent(self, res_name):
        for res in self.hydro_system.reservoirs:
            if res.name == res_name:
                return res.energy_equivalent

    def eval_report(self, scaled_price, price, actions, inflows):
        if self.report_df is None:
            self.init_eval_report(actions, inflows)

        state = self.hydro_system.report_state(actions)

        sum_money = 0
        sum_mega_watt_hours = 0

        for col, value in state.items():
            if ReportName.power in col:
                sum_mega_watt_hours += value * self.time_indexer.step_size_hours[self.current_step]
                sum_money += value * price * self.time_indexer.step_size_hours[self.current_step]

            self.report_df[col][self.current_step] = value

        self.report_df[ReportName.sum_money][self.current_step] = sum_money
        self.report_df[ReportName.energy_price][self.current_step] = price
        self.report_df[ReportName.scaled_energy_price][self.current_step] = scaled_price
        self.report_df[ReportName.sum_mwh][self.current_step] = sum_mega_watt_hours
        self.report_df[ReportName.end_value + "_" + self.end_value_calculation.end_type][
            self.current_step
        ] = self.end_reward

        for key, value in inflows.items():
            self.report_df[ReportName.inflow + key][self.current_step] = value
