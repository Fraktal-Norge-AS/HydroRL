"""
Module containing connection classes, used for different connections between hydro nodes.
"""
from typing import Union, Optional
from abc import ABCMeta, abstractproperty
from hps.system.nodes.base_node import IHydroNode


class IHydroEdge(metaclass=ABCMeta):
    """
    Edge between nodes in a hydropower system.
    :meta private:
    """

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def parent(self):
        pass

    @abstractproperty
    def child(self):
        pass

    @abstractproperty
    def max_flow(self):
        pass

    @abstractproperty
    def min_flow(self):
        pass


class BaseHydroEdge(IHydroEdge):
    """
    Base class for edges in the hydro system.
    :meta private:
    """

    def __init__(
        self,
        parent: IHydroNode,
        child: IHydroNode,
        min_flow: Union[int, float],
        max_flow: Union[int, float],
        name: Optional[str] = None,
    ):
        if min_flow > max_flow and min_flow < 0:
            raise ValueError("min_flow cannot be greater than max_flow")
        self._max_flow = max_flow
        self._min_flow = min_flow

        self._name = name or parent.name + " -> " + child.name

        if parent == child:
            raise ValueError("parent and child parameter cannot be the same.")
        self._parent = parent
        self._child = child

    @property
    def name(self):
        return self._name

    @property
    def min_flow(self):
        return self._min_flow

    @property
    def max_flow(self):
        return self._max_flow

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value: IHydroNode):
        assert isinstance(value, IHydroNode), "Parent node has to be of type 'IHydroNode'"
        self._parent = value

    @property
    def child(self):
        return self._child

    @child.setter
    def child(self, value: IHydroNode):
        assert isinstance(value, IHydroNode), "Child node has to be of type 'IHydroNode'"
        self._child = value

    def __str__(self):
        return "Bypass: {}".format(self.name)

    def to_dict(self):
        dct = {}
        dct["parent"] = self.parent.name
        dct["child"] = self.child.name
        dct["min_flow"] = self.min_flow
        dct["max_flow"] = self.max_flow
        dct["name"] = self.name

        return {type(self).__name__: dct}
