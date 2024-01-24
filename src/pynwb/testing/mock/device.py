from typing import Optional

from ... import NWBFile
from ...device import Device

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
