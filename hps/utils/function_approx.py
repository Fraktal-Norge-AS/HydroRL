from abc import ABCMeta, abstractmethod
from scipy.interpolate import CubicSpline
import numpy as np


class IFunctionApprox(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, x, y):
        pass

    @abstractmethod
    def get_y(self, x):
        pass


class BaseFunctionApprox(IFunctionApprox):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        x_lst = list(self.x)
        y_lst = list(self.y)
        return "{cls_name}(x={x}, y={y})".format(cls_name=type(self).__name__, x=x_lst, y=y_lst)

    def to_dict(self):
        dct = dict()
        dct["x"] = self.x
        dct["y"] = self.y

        return {type(self).__name__: dct}


class LinearFunctionApprox(BaseFunctionApprox):
    def __init__(self, x, y):
        super().__init__(x, y)

    def get_y(self, x):
        y = np.interp(x, self.x, self.y, left=self.y[0], right=self.y[-1])
        return y


class SplineFunctionApprox(BaseFunctionApprox):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.cubic_spline = CubicSpline(self.x, self.y)

    def get_y(self, x):
        y = self.cubic_spline(x)
        return y
