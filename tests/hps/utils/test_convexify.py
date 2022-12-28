import numpy as np

from hps.utils.convexify import convexify_1d


def test_convexify_1d():

    y_nonconvex = np.array([0.1, 0.2, 0.1, 0.15])
    y_convex = convexify_1d(y_nonconvex)

    y_exp = np.array([0.2, 0.2, 0.15, 0.15])

    np.testing.assert_equal(y_convex, y_exp)