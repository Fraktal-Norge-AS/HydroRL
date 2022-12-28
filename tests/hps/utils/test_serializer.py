import pytest
import json
import numpy as np
from hps.utils.serializer import HydroSystemSerializer


def test_serializer_numpy_array():
    
    class Dummy():
        def __init__(self):
            self.x = np.array([1,2])

        def to_dict(self):
            return {"Dummy": {"x": self.x}}

        
    dummy = Dummy()
    ser = HydroSystemSerializer.serialize(dummy)
    actual = HydroSystemSerializer.deserialize(ser)

    expected = dummy.to_dict()

    assert str(actual) == str(expected)


def test_ser_hs():
    from hydro_system_models import hydro_system_small, hydro_system_large, hydro_system_medium
    
    hydro_systems = [hydro_system_small(), hydro_system_medium(), hydro_system_large()]
    for hs in hydro_systems:
        hs_json = HydroSystemSerializer.serialize(hs)
        hs_ = HydroSystemSerializer.deserialize(hs_json)

        hs__json = HydroSystemSerializer.serialize(hs_)
        hs__ = HydroSystemSerializer.deserialize(hs__json)

        assert HydroSystemSerializer.serialize(hs__) == hs__json
