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


def mock_ElectrodeTable(n_rows=5, group=None):
    table = ElectrodeTable()
    group = group if group is not None else mock_ElectrodeGroup()
    for i in range(n_rows):
        table.add_row(
            location="CA1",
            group=group,
            group_name=group.name,
        )
    return table


def mock_electrodes(n_electrodes=5, table=mock_ElectrodeTable(n_rows=5)):
    return DynamicTableRegion(
        name="electrodes",
        data=list(range(n_electrodes)),
        description="the first and third electrodes",
        table=table,
    )


def mock_ElectricalSeries(
    name=None,
    description="description",
    data=None,
    rate=30000.0,
    timestamps=None,
    electrodes=None,
    filtering="filtering",
):
    return ElectricalSeries(
        name=name or name_generator("ElectricalSeries"),
        description=description,
        data=data if data is not None else np.ones((10, 5)),
        rate=rate,
        timestamps=timestamps,
        electrodes=electrodes or mock_electrodes(),
        filtering=filtering,
    )


def mock_SpikeEventSeries(
    name=None,
    description="description",
    data=None,
    timestamps=np.arange(10).astype(float),
    electrodes=None,
):
    return SpikeEventSeries(
        name=name or name_generator("SpikeEventSeries"),
        description=description,
        data=data if data is not None else np.ones((10, 5)),
        timestamps=timestamps if timestamps is not None else np.arange(10).astype(float),
        electrodes=electrodes if electrodes is not None else mock_electrodes(),
    )
