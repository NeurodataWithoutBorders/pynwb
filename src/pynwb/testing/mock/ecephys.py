from typing import Optional

import numpy as np

from hdmf.common.table import DynamicTableRegion, DynamicTable

from ...device import Device
from ...file import ElectrodeTable, NWBFile
from ...ecephys import ElectricalSeries, ElectrodeGroup, SpikeEventSeries
from .device import mock_Device
from .utils import name_generator
from ...misc import Units


def mock_ElectrodeGroup(
    name: Optional[str] = None,
    description: str = "description",
    location: str = "location",
    device: Optional[Device] = None,
    position: Optional[str] = None,
    nwbfile: Optional[NWBFile] = None,
) -> ElectrodeGroup:

    electrode_group = ElectrodeGroup(
        name=name or name_generator("ElectrodeGroup"),
        description=description,
        location=location,
        device=device or mock_Device(nwbfile=nwbfile),
        position=position,
    )

    if nwbfile is not None:
        nwbfile.add_electrode_group(electrode_group)

    return electrode_group


def mock_ElectrodeTable(
        n_rows: int = 5, group: Optional[ElectrodeGroup] = None, nwbfile: Optional[NWBFile] = None
) -> DynamicTable:
    electrodes_table = ElectrodeTable()
    group = group if group is not None else mock_ElectrodeGroup(nwbfile=nwbfile)
    for i in range(n_rows):
        electrodes_table.add_row(
            location="CA1",
            group=group,
            group_name=group.name,
        )

    if nwbfile is not None:
        nwbfile.electrodes = electrodes_table

    return electrodes_table


def mock_electrodes(
        n_electrodes: int = 5, table: Optional[DynamicTable] = None, nwbfile: Optional[NWBFile] = None
) -> DynamicTableRegion:

    table = table or mock_ElectrodeTable(n_rows=5, nwbfile=nwbfile)
    return DynamicTableRegion(
        name="electrodes",
        data=list(range(n_electrodes)),
        description="the first and third electrodes",
        table=table,
    )


def mock_ElectricalSeries(
    name: Optional[str] = None,
    description: str = "description",
    data=None,
    rate: Optional[float] = None,
    timestamps=None,
    starting_time: Optional[float] = None,
    electrodes: Optional[DynamicTableRegion] = None,
    filtering: str = "filtering",
    nwbfile: Optional[NWBFile] = None,
    channel_conversion: Optional[np.ndarray] = None,
    conversion: float = 1.0,
    offset: float = 0.,
) -> ElectricalSeries:
    
    # Set a default rate if timestamps are not provided
    rate = 30_000.0 if (timestamps is None and rate is None) else rate

    electrical_series = ElectricalSeries(
        name=name or name_generator("ElectricalSeries"),
        description=description,
        data=data if data is not None else np.ones((10, 5)),
        rate=rate,
        starting_time=starting_time,
        timestamps=timestamps,
        electrodes=electrodes or mock_electrodes(nwbfile=nwbfile),
        filtering=filtering,
        conversion=conversion,
        offset=offset,
        channel_conversion=channel_conversion,
    )

    if nwbfile is not None:
        nwbfile.add_acquisition(electrical_series)

    return electrical_series


def mock_SpikeEventSeries(
    name: Optional[str] = None,
    description: str = "description",
    data=None,
    timestamps=np.arange(10).astype(float),
    electrodes: Optional[DynamicTableRegion] = None,
    nwbfile: Optional[NWBFile] = None,
) -> SpikeEventSeries:
    spike_event_series = SpikeEventSeries(
        name=name or name_generator("SpikeEventSeries"),
        description=description,
        data=data if data is not None else np.ones((10, 5)),
        timestamps=timestamps if timestamps is not None else np.arange(10).astype(float),
        electrodes=electrodes if electrodes is not None else mock_electrodes(nwbfile=nwbfile),
    )

    if nwbfile is not None:
        nwbfile.add_acquisition(spike_event_series)

    return spike_event_series


def mock_Units(
    num_units: int = 10,
    max_spikes_per_unit: int = 10,
    seed: int = 0,
    nwbfile: Optional[NWBFile] = None,
) -> Units:

    units_table = Units(name="units")  # This is for nwbfile.units= mock_Units() to work
    units_table.add_column(name="unit_name", description="a readable identifier for the unit")

    rng = np.random.default_rng(seed=seed)

    times = rng.random(size=(num_units, max_spikes_per_unit)).cumsum(axis=1)
    spikes_per_unit = rng.integers(1, max_spikes_per_unit, size=num_units)

    spike_times = []
    for unit_index in range(num_units):

        # Not all units have the same number of spikes
        spike_times = times[unit_index, : spikes_per_unit[unit_index]]
        unit_name = f"unit_{unit_index}"
        units_table.add_unit(spike_times=spike_times, unit_name=unit_name)

    if nwbfile is not None:
        nwbfile.units = units_table

    return units_table
