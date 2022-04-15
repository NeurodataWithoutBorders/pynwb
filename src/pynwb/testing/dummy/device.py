import itertools

from ...device import Device


def name_device():
    for i in itertools.count(start=1):
        yield f"Device{i}"


device_name = name_device()


def make_Device(
    name=next(device_name),
    description="description",
    manufacturer=None,
):
    return Device(
        name=name,
        description=description,
        manufacturer=manufacturer,
    )
