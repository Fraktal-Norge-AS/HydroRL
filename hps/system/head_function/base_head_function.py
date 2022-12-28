from abc import ABCMeta, abstractclassmethod, abstractproperty, abstractmethod
from hps.utils.function_approx import IFunctionApprox
import numpy as np


class IHeadFunction(metaclass=ABCMeta):
    @abstractproperty
    def hrv(self):
        """
        Høyeste Regulerende Vannstand (LRV)
        """
        pass

    @abstractproperty
    def lrv(self):
        """
        Laveste Regulerende Vannstand (LRV)
        """
        pass

    @abstractproperty
    def v_min(self):
        pass

    @abstractproperty
    def v_max(self):
        pass

    @abstractmethod
    def get_head(self, volume):
        pass


class BaseHeadFunction(IHeadFunction):
    def __init__(self, lrv, hrv, v_min, v_max):
        """Base head function class.

        :param lrv: Lowest Regulating Waterheight
        :param hrv: Highest Regulating Waterheight
        :param v_min: Minimum reservoir volume
        :param v_max: Maximum reservoir volume
        :raises ValueError: If lrv > hrv
        """
        if hrv < lrv:
            raise ValueError(f"lrv {lrv} has to be lower than hrv {hrv}.")
        self._lrv = lrv
        self._hrv = hrv

        if v_max <= v_min:
            raise ValueError(f"v_min {v_min} has to be lower than v_max {v_max}.")

        self._v_min = v_min
        self._v_max = v_max

    def __repr__(self):
        return "head = {cls_name}(lrv={lrv}, hrv={hrv}, v_min={v_min}, v_max={v_max})".format(
            cls_name=type(self).__name__, lrv=self.lrv, hrv=self.hrv, v_min=self.v_min, v_max=self.v_max
        )

    @property
    def lrv(self):
        return self._lrv

    @property
    def hrv(self):
        return self._hrv

    @property
    def v_min(self):
        return self._v_min

    @property
    def v_max(self):
        return self._v_max

    def get_head(self, volume):
        raise NotImplementedError("To be implemented by subclass")


def head_decorator(func):
    def wrapper(self, volume):
        if volume < self.v_min:
            raise ValueError("Volume {} cannot be lower than v_min {}".format(volume, self.v_min))
        elif volume > self.v_max:
            raise ValueError("Volume {} cannot be higher than v_max {}".format(volume, self.v_max))

        head = func(self, volume)

        if head < self.lrv:
            raise ValueError("Head {} cannot be lower than lrv {}".format(head, self.lrv))
        # elif head > self.hrv:
        #     raise ValueError("Head {} cannot be higher than hrv {}".format(head, self.hrv))
        return head

    return wrapper


class HeadFunction(BaseHeadFunction):
    def __init__(self, lrv, hrv, v_min, v_max, head: IFunctionApprox):
        super().__init__(lrv, hrv, v_min, v_max)
        self.head = head

    @head_decorator
    def get_head(self, volume):
        head = self.head.get_y(x=volume)
        return head

    def __repr__(self):
        ret_str = "head_approx = " + str(self.head) + "\n"
        ret_str += "head = {cls_name}(lrv={lrv}, hrv={hrv}, v_min={v_min}, v_max={v_max}, head=head_approx)".format(
            cls_name=type(self).__name__, lrv=self.lrv, hrv=self.hrv, v_min=self.v_min, v_max=self.v_max
        )
        return ret_str

    def to_dict(self):
        dct = {}
        dct["lrv"] = self.lrv
        dct["hrv"] = self.hrv
        dct["v_min"] = self.v_min
        dct["v_max"] = self.v_max
        dct["head"] = self.head

        return {type(self).__name__: dct}


class ConstantHeadFunction(BaseHeadFunction):
    def __init__(self, head, v_min, v_max):
        """
        Class to generate a constant head function.
        Describing how head relates to volume for a reservoir.

        :param head: Constant head
        :param v_min: Minimum reservoir volume
        :param v_max: Maximum reservoir volume
        """
        super().__init__(head, head, v_min, v_max)

    @head_decorator
    def get_head(self, volume):
        head = self.lrv
        return head

    def __repr__(self):
        return "head = {cls_name}(head={head}, v_min={v_min}, v_max={v_max})".format(
            cls_name=type(self).__name__, head=self.lrv, v_min=self.v_min, v_max=self.v_max
        )

    def to_dict(self):
        dct = {}
        dct["head"] = self.lrv
        dct["v_min"] = self.v_min
        dct["v_max"] = self.v_max

        return {type(self).__name__: dct}


class LinearHeadFunction(BaseHeadFunction):
    def __init__(self, lrv, hrv, v_min, v_max):
        """
        Class to generate a linear head function.
        Describing how head relates to volume for a reservoir.

        :param lrv: Lowest Regulating Waterheight
        :param hrv: Highest Regulating Waterheight
        :param v_min: Minimum reservoir volume
        :param v_max: Maximum reservoir volume
        """
        super().__init__(lrv, hrv, v_min, v_max)
        self.weight = (self.hrv - self.lrv) / (self.v_max - self.v_min)
        self.bias = self.lrv - self.weight * self.v_min

    @head_decorator
    def get_head(self, volume):
        head = self.weight * volume + self.bias
        return head

    def to_dict(self):
        dct = {}
        dct["lrv"] = self.lrv
        dct["hrv"] = self.hrv
        dct["v_min"] = self.v_min
        dct["v_max"] = self.v_max

        return {type(self).__name__: dct}


class ExpHeadFunction(BaseHeadFunction):
    def __init__(self, lrv, hrv, v_min, v_max, decay=0.01):
        """
        Class to generate an exponential decreasing head function.
        Describing how head relates to volume for a reservoir.

        :param lrv: Lowest Regulating Waterheight
        :param hrv: Highest Regulating Waterheight
        :param v_min: Minimum reservoir volume
        :param v_max: Maximum reservoir volume
        """

        super().__init__(lrv, hrv, v_min, v_max)
        self.decay = decay
        max_exp_head = self._exp_func(self.v_max, (self.hrv - self.lrv), self.decay, self.lrv)

        # There is a small difference between hrv and max head from the exponential function
        # Adjust this by adding a linear term to the head function
        self.adjustment_weight = (self.hrv - max_exp_head) / (self.v_max - self.v_min)

    @head_decorator
    def get_head(self, volume):
        head = self._exp_func(volume, (self.hrv - self.lrv), self.decay, self.lrv) + self.adjustment_weight * volume
        return head

    def _exp_func(self, x, a, b, c):
        """Exponentially decreasing function.

        :param x: Function variable
        :param a: Height
        :param b: Decay
        :param c: Bias
        :return: Function value
        """
        return a * (1 - np.exp(-b * x)) + c

    def to_dict(self):
        dct = {}
        dct["lrv"] = self.lrv
        dct["hrv"] = self.hrv
        dct["v_min"] = self.v_min
        dct["v_max"] = self.v_max
        dct["decay"] = self.decay

        return {type(self).__name__: dct}
