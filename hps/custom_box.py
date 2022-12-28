import numpy as np
from gym.spaces import Box

from hps.rl.environment.hscomponents import DischargeAction, PickGateAction, StationAction, VariableInflowAction


class CustomSimpleBox(Box):
    def __init__(self, low, high, shape=None, dtype=np.float32, activation_chance=1):
        self.provide_zero_actions = False
        self.has_flipped = False
        self.start_point = 0
        self.activation_chance = activation_chance
        self.bit_generator = np.random.PCG64(seed=42)

        super(CustomBox, self).__init__(low, high, shape, dtype)

    def sample(self):
        values = Box.sample(self)
        if np.random.Generator(bit_generator=self.bit_generator).uniform(low=0, high=1) > self.activation_chance:
            values.fill(0.0)

        return values


class CustomBox(Box):
    def __init__(self, low, high, environment, is_eval, shape=None, dtype=np.float32):
        self.good_price_steps = []
        self.best_price_steps = []
        self.current_step = 0
        self.is_eval = is_eval
        self.relvol = 0

        self.station_action_indices = []
        action_index = 0

        for a in environment.hydro_system.sorted_actions:
            if isinstance(a, StationAction):
                self.station_action_indices.append(action_index)
                action_index += 1
            elif isinstance(a, PickGateAction):
                num_actions = len(a.input_actions)
                action_index += num_actions + 1
            elif isinstance(a, VariableInflowAction):
                pass
            elif isinstance(a, DischargeAction):
                action_index += 1

        print("Station action indices", self.station_action_indices)

        super(CustomBox, self).__init__(low, high, shape, dtype)

    def set_step(self, step, observations):
        if self.is_eval:
            return
        self.current_step = step
        self.observations = observations

        relvol = 0
        count = 0
        for key, value in observations.items():
            if key.startswith("relvol_"):
                relvol += value
                count += 1

        self.relvol = relvol / count

    def new_episode(self, price_list):
        if self.is_eval:
            return
        num_steps = len(price_list)

        prices = np.array(price_list)
        self.good_price_steps = prices.argsort()[-num_steps // 2 :][::-1]
        self.best_price_steps = prices.argsort()[-num_steps // 10 :][::-1]
        self.good_price_steps.sort()
        self.best_price_steps.sort()

        print("Price steps", self.good_price_steps)

    def sample(self):
        values = Box.sample(self)
        return values

        if self.is_eval:
            return values

        for sa in self.station_action_indices:
            if self.current_step in self.best_price_steps:
                values[sa] = 1.0
            elif self.current_step in self.good_price_steps:
                if self.relvol > 0.8:
                    values[sa] = 0.8
                elif self.relvol > 0.7:
                    values[sa] = 0.5
                else:
                    values[sa] = 0.0
            else:
                if self.relvol > 0.95:
                    values[sa] = 1.0
                else:
                    values[sa] = 0.0

        return values
