from abc import ABCMeta

from .base_node import IHydroNode


class IGate(metaclass=ABCMeta):
    """
    :meta private:
    """

    pass


class Gate(IHydroNode, IGate):
    """
    Class defining a gate.
    """

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self):
        return self._name

    def to_dict(self):
        return {type(self).__name__: {"name": self.name}}
