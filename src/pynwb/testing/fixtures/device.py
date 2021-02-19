import pytest

from ...device import Device


@pytest.fixture()
def device():
    return Device(name='device_name')
