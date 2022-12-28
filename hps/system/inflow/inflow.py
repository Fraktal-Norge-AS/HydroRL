from abc import ABCMeta, abstractmethod, abstractproperty
from typing import Union


class IInflow(metaclass=ABCMeta):
    @abstractproperty
    def series_id(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass


class NullInflow(IInflow):
    @property
    def series_id(self):
        pass

    def __repr__(self):
        return f"inflow_model = {type(self).__name__}()"

    def to_dict(self):
        dct = dict()
        return {type(self).__name__: dct}


class SimpleInflowModel(IInflow):
    def __init__(self, mean_yearly_inflow: Union[int, float], series_id: Union[int, str]):
        self._mean_yearly_inflow = mean_yearly_inflow
        self._series_id = series_id

    @property
    def mean_yearly_inflow(self):
        return self._mean_yearly_inflow

    @property
    def series_id(self):
        return self._series_id

    def __repr__(self):
        return 'inflow_model = {cls_name}(mean_yearly_inflow={mean_yearly_inflow}, series_id="{series_id}")'.format(
            cls_name=type(self).__name__, mean_yearly_inflow=self.mean_yearly_inflow, series_id=self.series_id
        )

    def to_dict(self):
        dct = dict()
        dct["mean_yearly_inflow"] = self.mean_yearly_inflow
        dct["series_id"] = self.series_id
        return {type(self).__name__: dct}


class ScaleInflowModel(IInflow):
    """
    Linking a inflow series with a scaling factor. Used when th inflow series id refers to a normalized inflow series,
    and the scaling factor is used to scale the inflow to a given reservoir/creek.
    """

    def __init__(self, scale_factor: float, series_id: Union[int, str], mean_yearly_inflow: Union[int, float]):
        self._mean_yearly_inflow = mean_yearly_inflow  # [Mm3]
        self._scale_factor = scale_factor
        self._series_id = series_id

    @property
    def series_id(self):
        return self._series_id

    @property
    def mean_yearly_inflow(self):
        return self._mean_yearly_inflow

    @property
    def scale_factor(self):
        return self._scale_factor

    def __repr__(self):
        return 'inflow_model = {cls_name}(scale_factor={scale_factor}, series_id="{series_id}", mean_yearly_inflow={mean_yearly_inflow})'.format(
            cls_name=type(self).__name__,
            scale_factor=self.scale_factor,
            series_id=self.series_id,
            mean_yearly_inflow=self.mean_yearly_inflow,
        )

    def to_dict(self):
        dct = dict()
        dct["scale_factor"] = self.scale_factor
        dct["series_id"] = self.series_id
        dct["mean_yearly_inflow"] = self.mean_yearly_inflow

        return {type(self).__name__: dct}


class ScaleYearlyInflowModel(IInflow):
    def __init__(self, mean_yearly_inflow):
        self._mean_yearly_inflow = mean_yearly_inflow  # [Mm3]
        self._mean_inflow = mean_yearly_inflow / (8760 * 3600 * 1e-6)  # [m3/s]
        self._series_id = None

    @property
    def mean_inflow(self):
        return self._mean_inflow

    @property
    def series_id(self):
        return self._series_id

    @property
    def mean_yearly_inflow(self):
        return self._mean_yearly_inflow

    @property
    def scale_factor(self):
        return self._scale_factor

    def __repr__(self):
        return "inflow_model = {cls_name}(mean_yearly_inflow={mean_yearly_inflow})".format(
            cls_name=type(self).__name__, mean_yearly_inflow=self.mean_yearly_inflow
        )

    def to_dict(self):
        dct = dict()
        dct["mean_yearly_inflow"] = self.mean_yearly_inflow

        return {type(self).__name__: dct}
