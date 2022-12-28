from abc import ABCMeta, abstractproperty


class IHydroNode(metaclass=ABCMeta):
    """
    :meta private:
    """

    @abstractproperty
    def name(self):
        pass
