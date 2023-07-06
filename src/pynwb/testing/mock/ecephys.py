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
        name=name if name is not None else name_generator("ElectrodeGroup"),
        description=description,
        location=location,
        device=device if device is not None else mock_Device(),
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
    group = group

    if group is not None:
        if group.parent is not None:
            if nwbfile is None:
                nwbfile = group.parent
                nwbfile.set_electrode_table(table)
            else:
                msg = "Group has NWBFile as parent already set. Use that for the NWBFile."
                raise ValueError(msg)
        else:
            if nwbfile is not None:
                nwbfile.add_electrode_group(group)
                nwbfile.set_electrode_table(table)
    else:
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


def mock_electrodes(n_electrodes=5, table=mock_ElectrodeTable(n_rows=5), nwbfile=None):
    if table.parent is not None and nwbfile is not None:
        msg = "The mock_ElectrodeTable already has an associated NWBFile."
        raise ValueError(msg)
    if table.parent is None and nwbfile is not None:
        nwbfile.set_electrode_table(table)


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
        name=name if name is not None else name_generator("ElectricalSeries"),
        description=description,
        data=data if data is not None else np.ones((10, 5)),
        rate=rate,
        timestamps=timestamps,
        electrodes=electrodes if electrodes is not None else mock_electrodes(),
        filtering=filtering,
    )

    if nwbfile is not None:
        if electrodes is None:
            if series.electrodes.table.group.parent is None:
                nwbfile.add_electrode_group(group)
                nwbfile.add_device(group.device)

            nwbfile.set_electrode_table(series.electrodes.table)
            nwbfile.add_acquisition(series)
        else:
            if series.electrodes.table.parent is not None:
                msg = "The mock_ElectrodeTable already has an associated NWBFile."
                raise ValueError(msg)
    else:
        if electrodes is not None:
            if series.electrodes.table.parent is not None:
                nwbfile = series.electrodes.table.parent
                nwbfile.add_acquisition(series)
    return series


def mock_SpikeEventSeries(
    name=None,
    description="description",
    data=None,
    timestamps=np.arange(10).astype(float),
    electrodes=None,
    nwbfile=None
):
    spike_event_series = SpikeEventSeries(
        name=name if name is not None else name_generator("SpikeEventSeries"),
        description=description,
        data=data if data is not None else np.ones((10, 5)),
        timestamps=timestamps if timestamps is not None else np.arange(10).astype(float),
        electrodes=electrodes if electrodes is not None else mock_electrodes(),
    )

    if nwbfile is not None:
        if electrodes is None:
            if spike_event_series.electrodes.table.group.parent is None:
                nwbfile.add_electrode_group(group)
                nwbfile.add_device(group.device)

            nwbfile.set_electrode_table(spike_event_series.electrodes.table)
            nwbfile.add_acquisition(spike_event_series)
        else:
            if spike_event_series.electrodes.table.parent is not None:
                msg = "The mock_ElectrodeTable already has an associated NWBFile."
                raise ValueError(msg)
    else:
        if electrodes is not None:
            if spike_event_series.electrodes.table.parent is not None:
                nwbfile = spike_event_series.electrodes.table.parent
                nwbfile.add_acquisition(spike_event_series)

    return spike_event_series
