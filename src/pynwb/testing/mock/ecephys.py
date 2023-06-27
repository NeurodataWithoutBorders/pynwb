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
    nwbfile=None
):
    electrode_group = ElectrodeGroup(
        name=name or name_generator("ElectrodeGroup"),
        description=description,
        location=location,
        device=device or mock_Device(),
        position=position,
    )
    if device is not None and device.parent is not None:
        if nwbfile is None:
            nwbfile = device.parent
            nwbfile.add_electrode_group(electrode_group)
        if nwbfile is not None:
            msg = "Device has NWBFile as parent already set. Use that for the NWBFile."
            raise ValueError(msg)        

    return electrode_group


def mock_ElectrodeTable(n_rows=5, group=None, nwbfile=None):
    table = ElectrodeTable()
    # group = group if group is not None else mock_ElectrodeGroup()
    group = group
    if group is not None and group.parent is not None:
        if nwbfile is None:
            nwbfile = group.parent
            nwbfile.set_electrode_table(table)
        else:
            msg = "Group has NWBFile as parent already set. Use that for the NWBFile."
            raise ValueError(msg)
    if group is not None and group.parent is None:
        if nwbfile is not None:
            nwbfile.add_electrode_group(group)
            nwbfile.set_electrode_table(table)
    if group is None:
        group = mock_ElectrodeGroup()
        if nwbfile is not None:
            nwbfile.add_electrode_group(group)
            nwbfile.set_electrode_table(table)

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
    nwbfile=None
):
    series = ElectricalSeries(
        name=name or name_generator("ElectricalSeries"),
        description=description,
        data=data if data is not None else np.ones((10, 5)),
        rate=rate,
        timestamps=timestamps,
        electrodes=electrodes or mock_electrodes(),
        filtering=filtering,
    )

    if nwbfile is not None and (electrodes is None or electrodes.table.parent is None):
        for group in series.electrodes.table.group.data:
            if group.parent==None:
                nwbfile.add_electrode_group(group)
                nwbfile.add_device(group.device)
            else:
                continue
        nwbfile.set_electrode_table(series.electrodes.table)
        nwbfile.add_acquisition(series)

    return series


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
