import numpy as np

from pynwb.file import ElectrodeTable

from pynwb.ecephys import ElectricalSeries, ElectrodeGroup, SpikeEventSeries
from hdmf.common.table import DynamicTableRegion
from .device import mock_Device
from .utils import name_generator




electrode_group_name = name_generator("ElectrodeGroup")


def mock_ElectrodeGroup(
    name=next(electrode_group_name),
    description="description",
    location="location",
    device=mock_Device(),
    position=None,
):
    return ElectrodeGroup(
        name=name, description=description, location=location, device=device, position=position,
    )


def mock_ElectrodeTable(n_rows=5, group=mock_ElectrodeGroup()):
    table = ElectrodeTable()
    for i in range(n_rows):
        table.add_row(
            x=1.0,
            y=2.0,
            z=3.0,
            imp=-(i + 1),
            location="CA1",
            filtering="none",
            group=group,
            group_name=group.name,
        )
    return table


def mock_electrodes(n_electrodes=5, table=mock_ElectrodeTable(n_rows=5)):
    return DynamicTableRegion(
        "electrodes", list(range(n_electrodes)), "the first and third electrodes", table
    )


def mock_ElectricalSeries(
    name="ElectricalSeries",
    description="description",
    data=np.ones((10, 5)),
    rate=30000.0,
    timestamps=None,
    electrodes=mock_electrodes(),
    filtering="filtering",
):
    return ElectricalSeries(
        name=name,
        description=description,
        data=data,
        rate=rate,
        timestamps=timestamps,
        electrodes=electrodes,
        filtering=filtering,
    )


def mock_SpikeEventSeries(
    name="ElectricalSeries",
    description="description",
    data=np.ones((10, 5)),
    timestamps=(1., 2., 3, 4., 5.),
    electrodes=mock_electrodes(),
):
    return SpikeEventSeries(
        name=name,
        description=description,
        data=data,
        timestamps=timestamps,
        electrodes=electrodes,
    )
