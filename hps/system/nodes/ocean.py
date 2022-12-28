from abc import ABCMeta

from .base_node import IHydroNode


class IOcean(metaclass=ABCMeta):
    """
    :meta private:
    """

    pass


class Ocean(IHydroNode, IOcean):
    """
    Class defining an ocean object. The end node(s) in a hydro system has to be an instance of this class.
    """

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self):
        return self._name

    def to_dict(self):
        return {type(self).__name__: {"name": self.name}}
