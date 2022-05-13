from ...device import Device

from .utils import name_generator


def mock_Device(
    name=name_generator("Device"),
    description="description",
    manufacturer=None,
):
    return Device(
        name=name,
        description=description,
        manufacturer=manufacturer,
    )
