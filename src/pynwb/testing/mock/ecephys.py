import numpy as np

from hdmf.common.table import DynamicTableRegion

from ...file import ElectrodeTable
from ...ecephys import ElectricalSeries, ElectrodeGroup, SpikeEventSeries
from .device import mock_Device
from .utils import name_generator


def mock_ElectrodeGroup(
    name=None,
    description="description",
    location="location",
    device=None,
    position=None,
):
    return ElectrodeGroup(
        name=name or name_generator("ElectrodeGroup"),
        description=description,
        location=location,
        device=device or mock_Device(),
        position=position,
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
    name=None,
    description="description",
    data=np.ones((10, 5)),
    rate=30000.0,
    timestamps=None,
    electrodes=None,
    filtering="filtering",
):
    return ElectricalSeries(
        name=name or name_generator("ElectricalSeries"),
        description=description,
        data=data,
        rate=rate,
        timestamps=timestamps,
        electrodes=electrodes or mock_electrodes(),
        filtering=filtering,
    )


def mock_SpikeEventSeries(
    name=None,
    description="description",
    data=np.ones((10, 5)),
    timestamps=np.arange(10).astype(float),
    electrodes=mock_electrodes(),
):
    return SpikeEventSeries(
        name=name or name_generator("SpikeEventSeries"),
        description=description,
        data=data,
        timestamps=timestamps,
        electrodes=electrodes,
    )
