from typing import Optional

import numpy as np

from pynwb.icephys import (
    IntracellularElectrode,
    VoltageClampSeries,
    VoltageClampStimulusSeries,
    IntracellularRecordingsTable,
    CurrentClampSeries,
    CurrentClampStimulusSeries,
    IZeroClampSeries,
)

from .utils import name_generator
from .device import mock_Device
from ... import NWBFile
from ...device import Device


def mock_IntracellularElectrode(
    name: Optional[str] = None,
        description: str = "description",
        device: Optional[Device] = None,
        nwbfile: Optional[NWBFile] = None,
) -> IntracellularElectrode:
    intracellular_electrode = IntracellularElectrode(
        name=name or name_generator("IntracellularElectrode"),
        description=description,
        device=device or mock_Device(nwbfile=nwbfile),
    )

    if nwbfile is not None:
        nwbfile.add_icephys_electrode(intracellular_electrode)

    return intracellular_electrode


def mock_VoltageClampStimulusSeries(
    name: Optional[str] = None,
    data=None,
    rate: float = 100_000.,
    electrode: Optional[IntracellularElectrode] = None,
    gain: float = 0.02,
    timestamps=None,
    starting_time: Optional[float] = None,
    nwbfile: Optional[NWBFile] = None,
) -> VoltageClampStimulusSeries:
    voltage_clamp_stimulus_series = VoltageClampStimulusSeries(
        name=name or name_generator("VoltageClampStimulusSeries"),
        data=data or np.ones((30,)),
        rate=None if timestamps else rate,
        electrode=electrode or mock_IntracellularElectrode(nwbfile=nwbfile),
        gain=gain,
        timestamps=timestamps,
        starting_time=starting_time,
    )

    if nwbfile is not None:
        nwbfile.add_stimulus(voltage_clamp_stimulus_series)

    return voltage_clamp_stimulus_series


def mock_VoltageClampSeries(
    name: Optional[str] = None,
    data=None,
    conversion: float = 1.0,
    resolution: float = np.nan,
    starting_time: Optional[float] = None,
    rate: Optional[float] = 100_000.0,
    electrode: Optional[IntracellularElectrode] = None,
    gain: float = 0.02,
    capacitance_slow: float = 100e-12,
    resistance_comp_correction: float = 70.0,
    nwbfile: Optional[NWBFile] = None,
) -> VoltageClampSeries:
    voltage_clamp_series = VoltageClampSeries(
        name=name if name is not None else name_generator("VoltageClampSeries"),
        data=data if data is not None else np.ones((30,)),
        conversion=conversion,
        resolution=resolution,
        starting_time=starting_time,
        rate=rate,
        electrode=electrode or mock_IntracellularElectrode(nwbfile=nwbfile),
        gain=gain,
        capacitance_slow=capacitance_slow,
        resistance_comp_correction=resistance_comp_correction,
    )

    if nwbfile is not None:
        nwbfile.add_acquisition(voltage_clamp_series)

    return voltage_clamp_series


def mock_CurrentClampSeries(
    name: Optional[str] = None,
    data=None,
    electrode: Optional[IntracellularElectrode] = None,
    gain: float = 0.02,
    stimulus_description: str = "N/A",
    bias_current=None,
    bridge_balance=None,
    capacitance_compensation=None,
    resolution=-1.0,
    conversion=1.0,
    timestamps=None,
    starting_time: Optional[float] = None,
    rate: Optional[float] = 100_000.,
    comments: str = "no comments",
    description: str = "no description",
    control=None,
    control_description=None,
    sweep_number=None,
    offset=0.0,
    unit: str = "volts",
    nwbfile: Optional[NWBFile] = None,
) -> CurrentClampSeries:
    current_clamp_series = CurrentClampSeries(
        name=name if name is not None else name_generator("CurrentClampSeries"),
        data=data if data is not None else np.ones((30,)),
        electrode=electrode or mock_IntracellularElectrode(nwbfile=nwbfile),
        gain=gain,
        stimulus_description=stimulus_description,
        bias_current=bias_current,
        bridge_balance=bridge_balance,
        capacitance_compensation=capacitance_compensation,
        resolution=resolution,
        conversion=conversion,
        timestamps=timestamps,
        starting_time=starting_time,
        rate=rate,
        comments=comments,
        description=description,
        control=control,
        control_description=control_description,
        sweep_number=sweep_number,
        offset=offset,
        unit=unit,
    )

    if nwbfile is not None:
        nwbfile.add_acquisition(current_clamp_series)

    return current_clamp_series


def mock_CurrentClampStimulusSeries(
    name: Optional[str] = None,
    data=None,
    electrode=None,
    gain=0.02,
    stimulus_description="N/A",
    resolution=-1.0,
    conversion=1.0,
    timestamps=None,
    starting_time=None,
    rate=100_000.,
    comments="no comments",
    description="no description",
    control=None,
    control_description=None,
    sweep_number=None,
    offset=0.0,
    unit="amperes",
    nwbfile: Optional[NWBFile] = None,
) -> CurrentClampStimulusSeries:
    current_clamp_stimulus_series = CurrentClampStimulusSeries(
        name=name or name_generator("CurrentClampStimulusSeries"),
        data=data if data is not None else np.ones((30,)),
        electrode=electrode or mock_IntracellularElectrode(nwbfile=nwbfile),
        gain=gain,
        stimulus_description=stimulus_description,
        resolution=resolution,
        conversion=conversion,
        timestamps=timestamps,
        starting_time=starting_time,
        rate=rate,
        comments=comments,
        description=description,
        control=control,
        control_description=control_description,
        sweep_number=sweep_number,
        offset=offset,
        unit=unit,
    )

    if nwbfile is not None:
        nwbfile.add_stimulus(current_clamp_stimulus_series)

    return current_clamp_stimulus_series


def mock_IZeroClampSeries(
    name: Optional[str] = None,
    data=None,
    electrode: Optional[IntracellularElectrode] = None,
    gain=.02,
    stimulus_description="N/A",
    resolution=-1.0,
    conversion=1.0,
    timestamps=None,
    starting_time=None,
    rate=100_000.,
    comments="no comments",
    description="no description",
    control=None,
    control_description=None,
    sweep_number=None,
    offset=0.0,
    unit="volts",
    nwbfile: Optional[NWBFile] = None,
) -> IZeroClampSeries:
    izero_clamp_series = IZeroClampSeries(
        name=name or name_generator("IZeroClampSeries"),
        data=data if data is not None else np.ones((30,)),
        electrode=electrode or mock_IntracellularElectrode(nwbfile=nwbfile),
        gain=gain,
        stimulus_description=stimulus_description,
        resolution=resolution,
        conversion=conversion,
        timestamps=timestamps,
        starting_time=starting_time,
        rate=rate,
        comments=comments,
        description=description,
        control=control,
        control_description=control_description,
        sweep_number=sweep_number,
        offset=offset,
        unit=unit,
    )

    if nwbfile is not None:
        nwbfile.add_acquisition(izero_clamp_series)

    return izero_clamp_series


def mock_IntracellularRecordingsTable(
    n_rows: int = 5, nwbfile: Optional[NWBFile] = None
) -> IntracellularRecordingsTable:
    irt = IntracellularRecordingsTable()
    for _ in range(n_rows):
        electrode = mock_IntracellularElectrode(nwbfile=nwbfile)
        irt.add_recording(
            electrode=electrode,
            stimulus=mock_VoltageClampStimulusSeries(electrode=electrode, nwbfile=nwbfile),
            response=mock_VoltageClampSeries(electrode=electrode, nwbfile=nwbfile),
        )

    if nwbfile is not None:
        nwbfile.intracellular_recordings = irt

    return irt
