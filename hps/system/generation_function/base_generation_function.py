from abc import ABCMeta, abstractmethod, abstractproperty


class IGenerationFunction(metaclass=ABCMeta):
    @abstractproperty
    def p_max(self):
        pass

    @abstractproperty
    def p_min(self):
        pass

    @abstractproperty
    def q_max(self):
        pass

    @abstractproperty
    def q_min(self):
        pass

    @abstractmethod
    def get_power(self, discharge, head=None):
        pass


class NullGenerationFunction(IGenerationFunction):
    @property
    def p_min(self):
        pass

    @property
    def p_max(self):
        pass

    @property
    def q_min(self):
        pass

    @property
    def q_max(self):
        pass

    def get_power(self, discharge, head=None):
        pass
