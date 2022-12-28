from typing import List, Union
from abc import ABCMeta, abstractmethod, abstractproperty

import pandas as pd
from pandas.core.indexes import period


class ITimeIndexer(metaclass=ABCMeta):
    @abstractproperty
    def index(self) -> pd.DatetimeIndex:
        pass

    @abstractproperty
    def from_datetime(self):
        pass

    @abstractproperty
    def to_datetime(self):
        pass

    @abstractproperty
    def length(self) -> int:
        pass

    @abstractproperty
    def step_size_hours(self) -> List:
        pass

    @abstractproperty
    def average_step_size_hours(self):
        pass

    @abstractproperty
    def sum_hours(self) -> float:
        pass


def compute_step_size_hours(index):
    step_size_hours = []
    for first, second in zip(index[:-1], index[1:]):
        step_size_hours.append((second - first) / pd.Timedelta(hours=1))
        if step_size_hours[-1] <= 0.0:
            raise ValueError("Step size cannot be nonpositive")
    return step_size_hours


class BaseTimeIndexer(ITimeIndexer):
    @property
    def from_datetime(self):
        return self._from_datetime

    @property
    def to_datetime(self):
        return self._to_datetime

    @property
    def length(self):
        return self._length

    @property
    def step_size_hours(self):
        return self._step_size_hours

    @property
    def sum_hours(self):
        return self._sum_hours

    @property
    def average_step_size_hours(self):
        return self._average_step_size_hours


class TimeIndexer(BaseTimeIndexer):
    def __init__(self, time_index):
        self.index = time_index

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value: Union[pd.DatetimeIndex, List]):
        self._index = pd.DatetimeIndex(value)
        self._from_datetime = self._index[0]
        self._to_datetime = self._index[-1]
        self._step_size_hours = compute_step_size_hours(self._index)
        self._length = len(self._step_size_hours)
        self._sum_hours = sum(self._step_size_hours)
        self._average_step_size_hours = self.sum_hours / self.length

    def get_nearest_step(self, date_time):
        loc = self._index.get_loc(date_time, method="nearest")
        return loc, self._index[loc]


class FromPeriodTimeIndexer(TimeIndexer):
    def __init__(self, from_datetime, periods, freq):
        super(FromPeriodTimeIndexer, self).__init__(pd.date_range(start=from_datetime, periods=periods + 1, freq=freq))


class FromToTimeIndexer(TimeIndexer):
    def __init__(self, from_datetime, to_datetime, periods):
        super(FromToTimeIndexer, self).__init__(
            pd.date_range(start=from_datetime, end=to_datetime, periods=periods + 1)
        )


class CombinedTimeIndexer(TimeIndexer):
    def __init__(self, from_datetime, first_periods, second_periods, first_freq, second_freq=None, to_datetime=None):
        if not second_freq and not to_datetime:
            raise TypeError("one of the arguments 'second_freq' or 'to_datetime' must be specified")
        elif second_freq and to_datetime:
            raise TypeError("only one of the arguments 'second_freq' or 'to_datetime' can have a value")

        first_time_index = FromPeriodTimeIndexer(from_datetime, first_periods, freq=first_freq)

        if to_datetime:
            second_time_index = FromToTimeIndexer(
                from_datetime=first_time_index.to_datetime, to_datetime=to_datetime, periods=second_periods
            )
        else:
            second_time_index = FromPeriodTimeIndexer(
                from_datetime=first_time_index.to_datetime, periods=second_periods, freq=second_freq
            )

        combined_time_index = first_time_index.index.append(second_time_index.index[1:])

        super(CombinedTimeIndexer, self).__init__(combined_time_index)


class MultipleCombinedTimeIndexer(TimeIndexer):
    def __init__(self, from_datetime: pd.Timestamp, periods: List, freqs: List):
        if len(periods) != len(freqs):
            raise TypeError("Lenght of 'periods' and 'freqs' has to be equal")
        combined_time_index = pd.DatetimeIndex([from_datetime])
        for period, freq in zip(periods, freqs):
            time_index = pd.date_range(start=combined_time_index[-1], periods=period + 1, freq=freq)
            combined_time_index = combined_time_index.append(time_index[1:])

        super(MultipleCombinedTimeIndexer, self).__init__(combined_time_index)
