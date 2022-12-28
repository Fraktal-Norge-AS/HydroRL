import logging
from abc import ABCMeta
from .base_generation_function import IGenerationFunction
from hps.utils.function_approx import IFunctionApprox


class IGenerationHeadFunction(metaclass=ABCMeta):
    pass


class BaseGenerationHeadFunction(IGenerationFunction, IGenerationHeadFunction):
    rho = 1e3  # [kg/m3]
    g = 9.81  # [m/s2]
    rho_g = rho * g / 1e6

    def __init__(self, q_min, q_max, p_min, p_max, logger=None):
        """
        :param q_min: Lower limit when in operation [m3/s]
        :param q_max: Upper limit when in operation [m3/s]
        :param p_min: Lower limit when in operation [MW]
        :param p_max: Upper limit when in operation [MW]
        """
        if p_min > p_max:
            raise ValueError("p_min cannot be larger than p_max.")
        if q_min > q_max:
            raise ValueError("q_min cannot be larger than q_max.")
        self.p_min = float(p_min)
        self.p_max = float(p_max)
        self.q_min = float(q_min)
        self.q_max = float(q_max)
        self.logger = logger or logging.getLogger(__name__)

    def __repr__(self):
        repr_str = "gen_func = "
        repr_str += "{cls_name}(q_min={q_min}, q_max={q_max}, p_min={p_min}, p_max={p_max})".format(
            cls_name=type(self).__name__, q_min=self.q_min, q_max=self.q_max, p_min=self.p_min, p_max=self.p_max
        )

        return repr_str

    def to_dict(self):
        dct = {}
        dct["q_min"] = self.q_min
        dct["q_max"] = self.q_max
        dct["p_max"] = self.p_max
        dct["p_min"] = self.p_min

        return {type(self).__name__: dct}

    @property
    def p_min(self):
        return self._p_min

    @p_min.setter
    def p_min(self, value):
        assert value >= 0.0
        self._p_min = value

    @property
    def p_max(self):
        return self._p_max

    @p_max.setter
    def p_max(self, value):
        assert value > self.p_min
        self._p_max = value

    @property
    def q_min(self):
        return self._q_min

    @q_min.setter
    def q_min(self, value):
        assert value >= 0.0
        self._q_min = value

    @property
    def q_max(self):
        return self._q_max

    @q_max.setter
    def q_max(self, value):
        assert value > self.q_min
        self._q_max = value

    def get_power(self, discharge, head):
        raise NotImplementedError("Should be implemented by subclass.")


class GenerationHeadFunction(BaseGenerationHeadFunction):
    def __init__(
        self,
        q_min,
        q_max,
        p_min,
        p_max,
        head_ref,
        q_ref,
        turb_eff: IFunctionApprox,
        gen_eff: IFunctionApprox,
        logger=None,
    ):
        super().__init__(q_min, q_max, p_min, p_max)
        self.turb_eff = turb_eff
        self.gen_eff = gen_eff
        self.head_ref = head_ref
        self.q_ref = q_ref

    def get_power(self, discharge, head):
        if discharge < self.q_min:
            power = 0.0
        else:
            n_turb = self.turb_eff.get_y(discharge) / 100
            power = n_turb * self.rho_g * (discharge) * (head)  # - head_losses?
            n_gen = self.gen_eff.get_y(power) / 100
            power = power * n_gen

        if power < self.p_min:
            power = 0.0
        elif power > self.p_max or discharge > self.q_max:
            power = self.p_max

        return power

    def __repr__(self):
        repr_str = "turb_eff = " + str(self.turb_eff) + "\n"
        repr_str += "gen_eff = " + str(self.gen_eff) + "\n"
        repr_str += "gen_func = "
        repr_str += "{cls_name}(q_min={q_min}, q_max={q_max}, p_min={p_min}, p_max={p_max}, head_ref={hr}, q_ref={qr}, turb_eff=turb_eff, gen_eff=gen_eff)".format(
            cls_name=type(self).__name__,
            q_min=self.q_min,
            q_max=self.q_max,
            p_min=self.p_min,
            p_max=self.p_max,
            hr=self.head_ref,
            qr=self.q_ref,
        )

        return repr_str

    def to_dict(self):
        dct = {}
        dct["q_min"] = self.q_min
        dct["q_max"] = self.q_max
        dct["p_max"] = self.p_max
        dct["p_min"] = self.p_min

        dct["head_ref"] = self.head_ref
        dct["q_ref"] = self.q_ref
        dct["turb_eff"] = self.turb_eff.to_dict()
        dct["gen_eff"] = self.gen_eff.to_dict()

        return {type(self).__name__: dct}


class VanillaGenerationHeadFunction(BaseGenerationHeadFunction):
    def __init__(self, q_min, q_max, p_min, p_max, eff: IFunctionApprox, logger=None):
        """
        Class for generating a generation function.
        Describing the power output of a power station wrt discharge and head

        :param eff: A function describing the efficiency
        """
        super().__init__(q_min, q_max, p_min, p_max, logger)
        self.eff = eff

    def get_power(self, discharge, head):
        if discharge < self.q_min:
            power = 0.0
        else:
            n = self.eff.get_y(discharge) / 100
            if n < 0.5 or n > 1.5:
                self.logger.warning("Efficiency not within reasonable bounds. Value is %f %", (n * 100))

            power = n * self.rho_g * (discharge) * (head)  # - head_losses?

        if power < self.p_min:
            power = 0.0
        elif power > self.p_max or discharge > self.q_max:
            power = self.p_max

        return power

    def __repr__(self):
        repr_str = "eff = " + str(self.eff) + "\n"
        repr_str += "gen_func = "
        repr_str += "{cls_name}(q_min={q_min}, q_max={q_max}, p_min={p_min}, p_max={p_max}, eff=eff)".format(
            cls_name=type(self).__name__,
            q_min=self.q_min,
            q_max=self.q_max,
            p_min=self.p_min,
            p_max=self.p_max,
        )

        return repr_str

    def to_dict(self):
        dct = {}
        dct["q_min"] = self.q_min
        dct["q_max"] = self.q_max
        dct["p_max"] = self.p_max
        dct["p_min"] = self.p_min
        dct["eff"] = self.eff.to_dict()

        return {type(self).__name__: dct}
