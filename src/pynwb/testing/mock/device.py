from ...device import Device

from .utils import name_generator


def mock_Device(
    name=None,
    description="description",
    manufacturer=None,
):
    return Device(
        name=name or name_generator("Device"),
        description=description,
        manufacturer=manufacturer,
    )
