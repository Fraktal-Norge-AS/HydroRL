import pytest

from hps.system.nodes import Ocean


@pytest.fixture()
def ocean():
    return Ocean(name="ocean1")


def test_name(ocean):
    assert ocean.name == "ocean1"
