import numpy as np
import pytest

@pytest.mark.skip
def test_get_observations(hsenv):

    vals = hsenv.get_observations(0)
    dct = hsenv.get_observations_dict(0)

    vals2 = np.array(list(dct.values()), dtype=np.float32)
    np.testing.assert_array_equal(vals, vals2)
