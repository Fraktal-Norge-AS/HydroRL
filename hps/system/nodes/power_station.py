from hps.system.generation_function.generation_head_function import IGenerationHeadFunction
from typing import Union, Optional
import logging

from abc import ABCMeta, abstractproperty
from hps.system.nodes.base_node import IHydroNode
from hps.system.generation_function import (
    IGenerationFunction,
    NullGenerationFunction,
)


class IPowerStation(metaclass=ABCMeta):
    """
    :meta private:
    """

    @abstractproperty
    def generation_function(self):
        pass

    @abstractproperty
    def start_cost(self):
        pass

    @abstractproperty
    def initial_state(self):
        pass

    @abstractproperty
    def energy_equivalent(self):
        pass


class PowerStation(IHydroNode, IPowerStation):
    """
    Class defining a power station.
    """

    def __init__(
        self,
        name: str,
        start_cost: Union[float, int],
        initial_state: bool,
        generation_function: Optional[IGenerationFunction] = None,
        nominal_head=None,
        nominal_discharge=None,
        energy_equivalent=None,
        logger=None,
    ):
        self.logger = logger or logging.getLogger(__name__)
        self._name = name
        self._start_cost = start_cost
        self._initial_state = initial_state
        self.generation_function = generation_function

        self.energy_equivalent = energy_equivalent
        self.nominal_head = nominal_head  # [h]
        self.nominal_discharge = nominal_discharge  # [m3/s]
        if energy_equivalent is not None:
            self.logger.info(
                f"Nominal values not used for computing energy equivalent for ({self}), as it is given as a parameter."
            )

        # Compute energy equivalent, with or without head dependency
        if (
            not isinstance(generation_function, NullGenerationFunction) and nominal_discharge
        ) and energy_equivalent is None:
            if isinstance(self.generation_function, IGenerationHeadFunction) and nominal_head:
                power = self.generation_function.get_power(discharge=self.nominal_discharge, head=self.nominal_head)
                self.energy_equivalent = power / (3.6 * self.nominal_discharge)  # [kWh/m3]

            elif isinstance(self.generation_function, IGenerationFunction):
                power = self.generation_function.get_power(discharge=self.nominal_discharge)
                self.energy_equivalent = power / (3.6 * self.nominal_discharge)  # [kWh/m3]

    @property
    def energy_equivalent(self):
        return self._energy_equivalent

    @energy_equivalent.setter
    def energy_equivalent(self, value):
        if value is not None:
            if value < 0 or value > 20:
                raise ValueError(f"Value for energy equivalent is not meaningful ({value})")
        self._energy_equivalent = value

    @property
    def name(self):
        return self._name

    @property
    def start_cost(self):
        return self._start_cost

    @property
    def initial_state(self):
        return self._initial_state

    @property
    def generation_function(self):
        return self._generation_function

    @generation_function.setter
    def generation_function(self, value):
        if isinstance(value, IGenerationFunction):
            self._generation_function = value
        else:
            self._generation_function = NullGenerationFunction()

    def to_dict(self):
        dct = {}
        dct["name"] = self.name
        dct["start_cost"] = self.start_cost
        dct["initial_state"] = self.initial_state
        dct["generation_function"] = self.generation_function.to_dict()
        dct["nominal_head"] = self.nominal_head
        dct["nominal_discharge"] = self.nominal_discharge
        dct["energy_equivalent"] = self.energy_equivalent

        return {type(self).__name__: dct}
