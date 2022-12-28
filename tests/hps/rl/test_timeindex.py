import pytest

import pandas as pd

from core.timeindex import (
    FromPeriodTimeIndexer, FromToTimeIndexer, CombinedTimeIndexer, TimeIndexer,
    MultipleCombinedTimeIndexer)


@pytest.fixture()
def time_indexer():
    time_index = ['2020-01-01 00:00:00+00:00', '2020-01-01 01:00:00+00:00',
               '2020-01-03 00:00:00+00:00', '2020-01-04 00:00:00+00:00',
               '2020-01-05 00:00:00+00:00', '2020-01-06 00:00:00+00:00',
               '2020-01-07 00:00:00+00:00', '2020-01-08 00:00:00+00:00',
               '2020-01-09 00:00:00+00:00', '2020-01-10 00:00:00+00:00']
    return TimeIndexer(time_index)

def test_timeindexer(time_indexer):
    time_index = ['2020-01-01 00:00:00+00:00', '2020-01-01 01:00:00+00:00',
               '2020-01-03 00:00:00+00:00', '2020-01-04 00:00:00+00:00',
               '2020-01-05 00:00:00+00:00', '2020-01-06 00:00:00+00:00',
               '2020-01-07 00:00:00+00:00', '2020-01-08 00:00:00+00:00',
               '2020-01-09 00:00:00+00:00', '2020-01-10 00:00:00+00:00']

    step_size_hours = [1.0, 47.0, 24.0, 24.0, 24.0, 24.0, 24.0, 24.0, 24.0]

    assert time_indexer.length == len(time_index) - 1
    assert time_indexer.from_datetime == pd.Timestamp(time_index[0])
    assert time_indexer.to_datetime == pd.Timestamp(time_index[-1])
    assert (time_indexer.index == pd.DatetimeIndex(time_index)).all()
    assert time_indexer.step_size_hours == step_size_hours
    assert time_indexer.average_step_size_hours == sum(step_size_hours)/len(step_size_hours)

def test_fromperiodtimeindexer():
    start = pd.Timestamp("2020-01-01T00:00:00Z")
    periods = 10
    freq = '1D'

    time_indexer = FromPeriodTimeIndexer(from_datetime=start, periods=periods, freq=freq)

    exp_index = pd.DatetimeIndex(['2020-01-01 00:00:00+00:00', '2020-01-02 00:00:00+00:00',
               '2020-01-03 00:00:00+00:00', '2020-01-04 00:00:00+00:00',
               '2020-01-05 00:00:00+00:00', '2020-01-06 00:00:00+00:00',
               '2020-01-07 00:00:00+00:00', '2020-01-08 00:00:00+00:00',
               '2020-01-09 00:00:00+00:00', '2020-01-10 00:00:00+00:00',
               '2020-01-11 00:00:00+00:00'])

    assert (time_indexer.index == exp_index).all()


def test_fromtotimeindexer():
    start = pd.Timestamp("2020-01-01T00:00:00Z")
    end = pd.Timestamp("2020-10-01T00:00:00Z")
    periods = 10
    
    time_indexer = FromToTimeIndexer(from_datetime=start, to_datetime=end, periods=periods)


    exp_index = pd.DatetimeIndex(['2020-01-01 00:00:00+00:00', '2020-01-28 09:36:00+00:00',
               '2020-02-24 19:12:00+00:00', '2020-03-23 04:48:00+00:00',
               '2020-04-19 14:24:00+00:00', '2020-05-17 00:00:00+00:00',
               '2020-06-13 09:36:00+00:00', '2020-07-10 19:12:00+00:00',
               '2020-08-07 04:48:00+00:00', '2020-09-03 14:24:00+00:00',
               '2020-10-01 00:00:00+00:00'])

    assert (time_indexer.index == exp_index).all()


def test_timeindexcombiner():
    start = pd.Timestamp("2020-01-01T00:00:00Z")
    end = pd.Timestamp("2020-10-01T00:00:00Z")
    first_periods = 2
    second_periods = 5
    first_freq = '1D'

    comb_time_indexer = CombinedTimeIndexer(start, first_periods, second_periods, first_freq, to_datetime=end)

    exp_index = pd.DatetimeIndex(['2020-01-01 00:00:00+00:00', '2020-01-02 00:00:00+00:00',
               '2020-01-03 00:00:00+00:00', '2020-02-26 09:36:00+00:00',
               '2020-04-20 19:12:00+00:00', '2020-06-14 04:48:00+00:00',
               '2020-08-07 14:24:00+00:00', '2020-10-01 00:00:00+00:00'])
    exp_step_size_hours = [24.0, 24.0, 1305.6, 1305.6, 1305.6, 1305.6, 1305.6]

    assert (comb_time_indexer.index == exp_index).all()
    assert comb_time_indexer.step_size_hours == exp_step_size_hours


def test_timeindexcombiner_periods():
#%%
    start = pd.Timestamp("2020-01-01T00:00:00Z")
    first_periods = 2
    second_periods = 5
    first_freq = '1D'
    second_freq = '2D'

    comb_time_indexer = CombinedTimeIndexer(start, first_periods, second_periods, first_freq, second_freq)

    exp_index = pd.DatetimeIndex(['2020-01-01 00:00:00+00:00', '2020-01-02 00:00:00+00:00',
               '2020-01-03 00:00:00+00:00', '2020-01-05 00:00:00+00:00',
               '2020-01-07 00:00:00+00:00', '2020-01-09 00:00:00+00:00',
               '2020-01-11 00:00:00+00:00', '2020-01-13 00:00:00+00:00'])

    assert (comb_time_indexer.index == exp_index).all()


def test_time_indexcombiner_fails():
    start = pd.Timestamp("2020-01-01T00:00:00Z")
    end = pd.Timestamp("2020-10-01T00:00:00Z")
    first_periods = 2
    second_periods = 5
    first_freq = '1D'
    second_freq = '2D'

    with pytest.raises(TypeError):
        CombinedTimeIndexer(start, first_periods, second_periods, first_freq)

    with pytest.raises(TypeError):
            CombinedTimeIndexer(start, first_periods, second_periods, first_freq, second_freq, end)


def test_multiple_combined_indexer():

    start = pd.Timestamp("2020-01-01T00:00:00Z")
    time_indexer = MultipleCombinedTimeIndexer(
        from_datetime=start,
        periods=[3, 10, 1],
        freqs=['8H', '1D', '2D'])

    exp_index = pd.DatetimeIndex(['2020-01-01 00:00:00+00:00', '2020-01-01 08:00:00+00:00',
                '2020-01-01 16:00:00+00:00', '2020-01-02 00:00:00+00:00',
                '2020-01-03 00:00:00+00:00', '2020-01-04 00:00:00+00:00',
                '2020-01-05 00:00:00+00:00', '2020-01-06 00:00:00+00:00',
                '2020-01-07 00:00:00+00:00', '2020-01-08 00:00:00+00:00',
                '2020-01-09 00:00:00+00:00', '2020-01-10 00:00:00+00:00',
                '2020-01-11 00:00:00+00:00', '2020-01-12 00:00:00+00:00',
                '2020-01-14 00:00:00+00:00'])


    assert (time_indexer.index == exp_index).all()

# %%

