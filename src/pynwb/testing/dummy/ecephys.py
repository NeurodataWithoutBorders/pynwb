import itertools

import numpy as np

from pynwb.file import ElectrodeTable

from pynwb.ecephys import ElectricalSeries, ElectrodeGroup, SpikeEventSeries
from hdmf.common.table import DynamicTableRegion
from .device import make_Device


def name_electrode_group():
    for i in itertools.count(start=1):
        yield f"ElectrodeGroup{i}"


electrode_group_name = name_electrode_group()


def make_ElectrodeGroup(
        name=next(electrode_group_name),
        description="description",
        location="location",
        device=make_Device(),
        position=None,
    ):
        return ElectrodeGroup(
            name=name, description=description, location=location, device=device, position=position,
        )


def make_electrode_table(n_rows=5, group=make_ElectrodeGroup()):
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


def make_electrodes(n_electrodes=5, table=make_electrode_table(n_rows=5)):
    return DynamicTableRegion(
        "electrodes", list(range(n_electrodes)), "the first and third electrodes", table
    )


def make_ElectricalSeries(
    name="ElectricalSeries",
    description="description",
    data=np.ones((10, 5)),
    rate=30000.0,
    timestamps=None,
    electrodes=make_electrodes(),
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


def make_SpikeEventSeries(
    name="ElectricalSeries",
    description="description",
    data=np.ones((10, 5)),
    rate=30000.0,
    timestamps=None,
    electrodes=make_electrodes(),
    filtering=None,
):
    return SpikeEventSeries(
        name=name,
        description=description,
        data=data,
        rate=rate,
        timestamps=timestamps,
        electrodes=electrodes,
        filtering=filtering,
    )
