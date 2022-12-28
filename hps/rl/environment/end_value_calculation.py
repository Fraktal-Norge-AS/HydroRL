from abc import abstractmethod, abstractproperty
import numpy as np

from hps.rl.environment.end_value_type import EndStateIncentive
from core.timeindex import TimeIndexer
from hps.rl.settings import ObservationSettings
from hps.rl.environment.observations_generator import ObservationsGenerator
from core.value_scaler import RewardScaler


class IEndValueCalculation(object):
    @abstractproperty
    def end_type(self):
        pass

    @abstractmethod
    def calculate(self, hydro_system, current_price, current_inflow, actions: np.ndarray):
        pass


class EmptyEndValueCalculation(IEndValueCalculation):
    def __init__(self):
        self._end_type = EndStateIncentive.Off

    @property
    def end_type(self):
        return self._end_type

    def calculate(self):
        return 0.0


class PriceEndValueCalculation(IEndValueCalculation):
    def __init__(self, end_type, reservoirs):
        self.reservoirs = reservoirs
        self._end_type = end_type

    @property
    def end_type(self):
        return self._end_type

    def calculate(self, price):
        end_reward = 0.0
        for res in [r for r in self.reservoirs if not r.is_ocean]:
            end_reward += (res.current_volume) * res.energy_equivalent * 10**3 * price

        return end_reward


class ProvidedPriceEndValueCalculation(IEndValueCalculation):
    def __init__(self, reservoirs, price):
        self.reservoirs = reservoirs
        self._end_type = EndStateIncentive.ProvidedEndEnergyPrice
        self.price = price

    @property
    def end_type(self):
        return self._end_type

    def calculate(self):
        end_reward = 0.0
        for res in [r for r in self.reservoirs if not r.is_ocean]:
            end_reward += (res.current_volume) * res.energy_equivalent * 10**3 * self.price

        return end_reward


class QEndValueCalculation(IEndValueCalculation):
    def __init__(
        self,
        past_observations_settings: ObservationSettings,
        current_time_indexer: TimeIndexer,
        past_time_indexer: TimeIndexer,
        tf_agent,
        maximum_production,
        past_reward_scale_factor,
    ):
        self._end_type = EndStateIncentive.QValue

        self.network_1 = tf_agent._target_critic_network_1.copy()
        self.network_2 = tf_agent._target_critic_network_2.copy()
        self.network_1.create_variables()
        self.network_2.create_variables()
        self.network_1.set_weights(tf_agent._target_critic_network_1.get_weights())
        self.network_2.set_weights(tf_agent._target_critic_network_2.get_weights())

        current_end_dt = current_time_indexer.to_datetime
        self.step_to_use, past_dt = past_time_indexer.get_nearest_step(current_end_dt)
        self.average_past_step_size = past_time_indexer.sum_hours / past_time_indexer.length

        if current_end_dt != past_dt:
            print("WARNING : Inexact step match, current end {} maps to {}".format(current_end_dt, past_dt))

        self.observations_generator = ObservationsGenerator(
            observation_settings=past_observations_settings, time_indexer=past_time_indexer, is_eval=True
        )

        self.reward_scaler = RewardScaler(
            maximum_production=maximum_production,
            num_steps=past_time_indexer.length,
            average_step_size_hours=past_time_indexer.average_step_size_hours,
            constant=past_reward_scale_factor,
        )

    @property
    def end_type(self):
        return self._end_type

    def calculate(self, hydro_system, current_price, current_inflow, actions: np.ndarray):
        observations = self.observations_generator.get_observations(
            self.step_to_use - 1, hydro_system, current_price, current_inflow
        )
        observations = np.array(observations)

        value = compute_q_value(self.network_1, self.network_2, actions, observations)

        return self.reward_scaler.descale(value)


# def compute_q_value(network_1, network_2, actions: np.ndarray, observations: np.ndarray):
#     """
#     Compute Q value for two critic networks. Given action and observation.
#     """

#     state = tf.convert_to_tensor(observations[np.newaxis], dtype=tf.float32)
#     action = tf.convert_to_tensor(actions[np.newaxis], dtype=tf.float32)

#     q_input = (state, action)
#     q_val1, _ = network_1(q_input)
#     q_val2, _ = network_2(q_input)
#     q_val = tf.minimum(q_val1, q_val2)

#     return q_val.numpy()[0]
