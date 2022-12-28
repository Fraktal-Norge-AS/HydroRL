import pytest

from hps.system.nodes import Gate


@pytest.fixture()
def gate():
    return Gate(name="gate1")


def test_name(gate):
    assert gate.name == "gate1"
