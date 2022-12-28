import numpy as np


def convexify_1d(y):
    """Return the convex representation of y.

    :param y: 1D data
    :type y: List or np.array
    :rtype: np.array
    """

    y = np.array(y)
    argmax = y.argmax()
    y[:argmax] = y.max()

    for i in reversed(range(argmax, len(y))):
        y[:i] = np.where(y[:i] < y[i], y[i], y[:i])

    return y
