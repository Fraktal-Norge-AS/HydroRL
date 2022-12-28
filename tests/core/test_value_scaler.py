import numpy as np
from core.value_scaler import (
    Discounter, LogScaler, ConstantScaler, NormalizeLogScaler, RewardScaler,
    PriceScaler)
from core.timeindex import TimeIndexer


def test_price_scaler():
    max_value = 150
    min_value = 30
    scale_by = 2
    scaler = PriceScaler(max_value=max_value, min_value=min_value, scale_by=scale_by)

    values = np.array([0, 30, 90, 150, 210])
    # exp_scaled = np.array([-60.,    0.,  120.,  240.,  360.])
    exp_descaled = values

    actual_scaled = np.zeros_like(values)
    actual_descaled = np.zeros_like(exp_descaled)
    for i, val in enumerate(values):
        actual_scaled[i] = scaler.scale(val)
        actual_descaled[i] = scaler.descale(actual_scaled[i])

    # np.testing.assert_almost_equal(actual_scaled, exp_scaled)
    np.testing.assert_almost_equal(actual_descaled, exp_descaled)


def test_normalize_log_scaler():
    scaler = NormalizeLogScaler(min_value=10, max_value=20)

    value = 13.2
    exp_scaled_value = 0.43815827

    scaled_value = scaler.scale(value)
    descaled_value = scaler.descale(scaled_value)

    np.testing.assert_almost_equal(exp_scaled_value, scaled_value)
    np.testing.assert_almost_equal(value, descaled_value)


def test_log():
    
    scaler = LogScaler(base_value=10)
    value = 14.
    scaled = scaler.scale(value)
    descaled = scaler.descale(scaled)
    
    np.testing.assert_almost_equal(value, descaled)

        
def test_log_scaled_value():
    value = 15
    base_value = 30 
    scaler = LogScaler(base_value)
    scaled_value = scaler.scale(value)
    
    exp_scaled = np.log(1 + value)/np.log(1 +  base_value)

    np.testing.assert_almost_equal(exp_scaled, scaled_value)

    
def test_constant():
    
    scaler = ConstantScaler(base_value=10)
    value = 14.
    scaled = scaler.scale(value)
    descaled = scaler.descale(scaled)
    
    np.testing.assert_almost_equal(value, descaled)


def test_reward_scaler():
    maximum_production = 100
    num_steps = 52
    average_step_size_hours = 168
    constant = 10
    
    rew_scaler =  RewardScaler(
        maximum_production=maximum_production,
        num_steps=num_steps,
        constant=constant,
        average_step_size_hours=average_step_size_hours)

    expected_value = 12
    scaled_value = rew_scaler.scale(expected_value)
    actual_value = rew_scaler.descale(scaled_value)

    np.testing.assert_almost_equal(actual_value, expected_value)


def test_discounter():
    discount_rate = 0.05

    #Expected discount values
    import pandas as pd
    step_size_hours = [3600, 2700, 2460] # Hours in steps            
    acc_step_size_hours = np.cumsum(step_size_hours)
    exp_discount = [1/(1+discount_rate)**(h/8760) for h in acc_step_size_hours]

    # Actual discount values
    time_index = pd.DatetimeIndex(["2020-01-01T00:00:00Z"])    
    time_index = time_index.append(pd.DatetimeIndex([time_index[0] + pd.Timedelta(hours=step_hours) for step_hours in acc_step_size_hours]))
    time_indexer = TimeIndexer(time_index)
    discounter = Discounter(discount_rate=discount_rate, time_indexer=time_indexer)
    actual_discount = [discounter.get_gamma(i) for i in range(time_indexer.length)]

    assert exp_discount == actual_discount