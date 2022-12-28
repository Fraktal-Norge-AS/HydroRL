from abc import ABCMeta, abstractproperty

from .base_generation_function import IGenerationFunction


class IConstantGenerationFunction(metaclass=ABCMeta):
    @abstractproperty
    def power_equivalent(self):
        pass


class ConstantGenerationFunction(IGenerationFunction, IConstantGenerationFunction):
    def __init__(self, p_min, p_max, power_equivalent):
        """
        :param p_min: Lower limit when in operation [MW]
        :param p_max: Upper limit when in operation [MW]
        :param power_eq: Power equivalent. [MW/(m3/s)]
        """
        if p_min > p_max:
            raise ValueError("p_min cannot be larger than p_max.")
        self._p_min = float(p_min)
        self._p_max = float(p_max)
        self._power_equivalent = power_equivalent

    def __repr__(self):
        return "{}(p_min={}, p_max={}, power_equivalent={})".format(
            type(self).__name__, self._p_min, self.p_max, self.power_equivalent
        )

    @property
    def p_min(self):
        return self._p_min

    @property
    def p_max(self):
        return self._p_max

    @property
    def q_min(self):
        return self._p_min / self.power_equivalent

    @property
    def q_max(self):
        return self._p_max / self.power_equivalent

    @property
    def power_equivalent(self):
        return self._power_equivalent

    def get_power(self, discharge, head=None):
        """
        Get the power for the given discharge.
        :param dishcarge: discharge [m3/s]
        :return: power [MW]
        """
        power = self.power_equivalent * discharge
        if power < self.p_min:
            power = 0.0
        elif power > self.p_max:
            power = self.p_max

        return power

    def to_dict(self):
        dct = {}
        dct["p_min"] = self.p_min
        dct["p_max"] = self.p_max

        dct["power_equivalent"] = self.power_equivalent

        return {type(self).__name__: dct}
