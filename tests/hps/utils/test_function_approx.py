import pytest


from hps.utils import SplineFunctionApprox, LinearFunctionApprox


@pytest.fixture()
def linear_func():
    x = [0,10]
    y = [50, 100]
    return LinearFunctionApprox(x=x,y=y)


def test_linear_approx(linear_func):
    expected = 75
    actual = linear_func.get_y(5)
    assert abs(expected - actual) < 1e-6
