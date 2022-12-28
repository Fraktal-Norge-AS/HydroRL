#%%
from abc import ABCMeta, abstractmethod
import numpy as np


class IBaseScaler(metaclass=ABCMeta):
    @abstractmethod
    def scale(self, value):
        pass

    @abstractmethod
    def descale(self, value):
        pass


class NormalizeLogScaler(IBaseScaler):
    """
    Log normalizer for values between 0 and 1.
    """

    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value

    def scale(self, value, clip=False):
        normalize_value = (value - self.min_value) / (self.max_value - self.min_value) * (np.e - 1)
        if clip:
            return np.clip(np.log(1 + normalize_value), 0, 1)
        else:
            return np.log(1 + normalize_value)

    def descale(self, value):
        return (self.max_value - self.min_value) * (np.e**value - 1) / (np.e - 1) + self.min_value


class LogScaler(IBaseScaler):
    def __init__(self, base_value):
        self.base_value = base_value

    def scale(self, value, clip=False):
        if clip:
            value = np.clip(value, a_min=0, a_max=self.base_value)
        return np.log(1 + value) / np.log(1 + self.base_value)

    def descale(self, value):
        return (1 + self.base_value) ** value - 1


class ConstantScaler(IBaseScaler):
    def __init__(self, base_value):
        self.base_value = base_value

    def scale(self, value, clip=False):
        if clip:
            value = np.clip(value, a_min=0, a_max=self.base_value)
        return value / self.base_value

    def descale(self, value):
        return self.base_value * value


class RewardScaler(IBaseScaler):
    def __init__(self, maximum_production, num_steps, average_step_size_hours, constant):
        self.scale_factor = maximum_production * average_step_size_hours * num_steps / constant

    def scale(self, reward):
        return reward / self.scale_factor

    def descale(self, scaled_reward):
        return scaled_reward * self.scale_factor


class PriceScaler(IBaseScaler):
    def __init__(self, max_value, min_value, scale_by):
        self.min_value = min_value
        self.max_value = max_value
        self.scale_by = scale_by

    def scale(self, price):
        return (price - self.min_value) * self.scale_by

    def descale(self, scaled_price):
        return scaled_price / self.scale_by + self.min_value


class IDiscounter(metaclass=ABCMeta):
    @abstractmethod
    def get_gamma(self, step):
        pass


class Discounter(IDiscounter):
    def __init__(self, discount_rate, time_indexer):
        """
        :param discount_rate: Yearly discount rate as fraction between 0 and 0.5.
        :param time_indexer: TimeIndexer
        """
        if not 0 <= discount_rate <= 0.5:
            raise ValueError("Discount rate should be between 0 and 0.5")

        self.discount_rate = discount_rate
        self.aggregated_step_hours = np.cumsum(time_indexer.step_size_hours)

    def get_gamma(self, step):
        exponent = self.aggregated_step_hours[step] / 8760
        return 1 / (1 + self.discount_rate) ** exponent
