from typing import Optional

from ... import NWBFile
from ...device import Device, DeviceModel

from .utils import name_generator


def mock_Device(
    name: Optional[str] = None,
    description: str = "description",
    manufacturer: Optional[str] = None,
    nwbfile: Optional[NWBFile] = None,
) -> Device:
    device = Device(
        name=name or name_generator("Device"),
        description=description,
        manufacturer=manufacturer,
    )

    if nwbfile is not None:
        nwbfile.add_device(device)

    return device


def mock_DeviceModel(
    name: Optional[str] = None,
    manufacturer: str = None,
    model_number: Optional[str] = None,
    description: str = "description",
    nwbfile: Optional[NWBFile] = None,
) -> DeviceModel:
    device = DeviceModel(
        name=name or name_generator("DeviceModel"),
        manufacturer=manufacturer,
        model_number=model_number,
        description=description,
    )

    if nwbfile is not None:
        nwbfile.add_device_model(device)

    return device
