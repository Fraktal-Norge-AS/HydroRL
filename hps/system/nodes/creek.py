from typing import Optional

from abc import ABCMeta, abstractproperty

from hps.system.nodes.base_node import IHydroNode
from hps.system.inflow import IInflow, NullInflow


class ICreek(metaclass=ABCMeta):
    """
    :meta private:
    """

    @abstractproperty
    def inflow_model(self):
        pass


class Creek(IHydroNode, ICreek):
    """
    Class defining a creek.
    """

    def __init__(self, name: str, inflow_model: Optional[IInflow] = None):
        self._name = name
        self.inflow_model = inflow_model

    @property
    def name(self):
        return self._name

    @property
    def inflow_model(self):
        return self._inflow_model

    @inflow_model.setter
    def inflow_model(self, value):
        if isinstance(value, IInflow):
            self._inflow_model = value
        else:
            self._inflow_model = NullInflow()

    def to_dict(self):
        return {type(self).__name__: {"name": self.name}, "inflow_model": self.inflow_model.to_dict()}
