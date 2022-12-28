from abc import ABCMeta, abstractproperty
import logging

from hps.system.nodes.base_node import IHydroNode
from hps.system.inflow import IInflow, NullInflow
from hps.system.head_function import IHeadFunction


class IReservoir(metaclass=ABCMeta):
    """
    :meta private:
    """

    @abstractproperty
    def max_volume(self):
        pass

    @abstractproperty
    def min_volume(self):
        pass

    @abstractproperty
    def inflow_model(self):
        pass

    @abstractproperty
    def tank_water_cost(self):
        pass

    @abstractproperty
    def energy_equivalent(self):
        pass

    @abstractproperty
    def price_of_spillage(self):
        pass


class Reservoir(IHydroNode, IReservoir):
    """
    Class defining a reservoir.
    """

    def __init__(
        self,
        name,
        min_volume,
        max_volume,
        inflow_model=None,
        tank_water_cost=1e6,
        head: IHeadFunction = None,
        energy_equivalent=None,
        price_of_spillage=1.0,
        logger=None,
    ):
        self.logger = logger or logging.getLogger(__name__)
        self.name = name

        if min_volume > max_volume:
            raise ValueError("min_volume cannot be larger than max_volume")
        self._min_volume = min_volume
        self._max_volume = max_volume        
        self.inflow_model = inflow_model
        self.tank_water_cost = tank_water_cost
        self.head = head
        self.energy_equivalent = energy_equivalent
        self.price_of_spillage = price_of_spillage

        if energy_equivalent is not None:
            self.logger.info(f"Energy equivalent for {self} is set, and will not be calculated.")

    @property
    def price_of_spillage(self):
        return self._price_of_spillage

    @price_of_spillage.setter
    def price_of_spillage(self, value):
        if value is not None:
            if value < 0 or value > 50:
                raise ValueError(f"Value for 'price_of_spillage' is not meaningful ({value})")
        self._price_of_spillage = value

    @property
    def energy_equivalent(self):
        return self._energy_equivalent

    @energy_equivalent.setter
    def energy_equivalent(self, value):
        if value is not None:
            if value < 0 or value > 20:
                raise ValueError(f"Value for 'energy_equivalent' is not meaningful ({value})")
        self._energy_equivalent = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self._name = value
        else:
            raise ValueError("property 'name' should be of type str.")

    @property
    def inflow_model(self):
        return self._inflow_model

    @inflow_model.setter
    def inflow_model(self, value):
        if isinstance(value, IInflow):
            self._inflow_model = value
        else:
            self._inflow_model = NullInflow()

    @property
    def min_volume(self):
        return self._min_volume

    @min_volume.setter
    def min_volume(self, value):
        if isinstance(value, (int, float)) and value < self.max_volume:
            self._min_volume = value
        else:
            raise ValueError("")

    @property
    def max_volume(self):
        return self._max_volume

    @max_volume.setter
    def max_volume(self, value):
        if isinstance(value, (int, float)) and value > self.min_volume:
            self._max_volume = value
        else:
            raise ValueError("")

    @property
    def tank_water_cost(self):
        return self._tank_water_cost

    @tank_water_cost.setter
    def tank_water_cost(self, value):
        self._tank_water_cost = value

    def to_dict(self):
        dct = {}
        dct["name"] = self.name
        dct["min_volume"] = self.min_volume
        dct["max_volume"] = self.max_volume
        dct["inflow_model"] = self.inflow_model.to_dict()
        dct["tank_water_cost"] = self.tank_water_cost

        dct["head"] = None
        if self.head:
            dct["head"] = self.head.to_dict()

        dct["energy_equivalent"] = self.energy_equivalent
        dct["price_of_spillage"] = self.price_of_spillage

        return {type(self).__name__: dct}
