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


def mock_IntracellularElectrode(
    name=None, description="description", device=None,
):
    return IntracellularElectrode(
        name=name or name_generator("IntracellularElectrode"),
        description=description,
        device=device or mock_Device(),
    )


def mock_VoltageClampStimulusSeries(
    name=None,
    data=None,
    rate=100_000.,
    electrode=None,
    gain=0.02,
    timestamps=None,
    starting_time=None,
):
    return VoltageClampStimulusSeries(
        name=name or name_generator("VoltageClampStimulusSeries"),
        data=data or np.ones((30,)),
        rate=None if timestamps else rate,
        electrode=electrode or mock_IntracellularElectrode(),
        gain=gain,
        timestamps=timestamps,
        starting_time=starting_time,
    )


def mock_VoltageClampSeries(
    name=None,
    data=None,
    conversion=1.0,
    resolution=np.nan,
    starting_time=None,
    rate=100_000.0,
    electrode=None,
    gain=0.02,
    capacitance_slow=100e-12,
    resistance_comp_correction=70.0,
):
    return VoltageClampSeries(
        name=name if name is not None else name_generator("VoltageClampSeries"),
        data=data if data is not None else np.ones((30,)),
        conversion=conversion,
        resolution=resolution,
        starting_time=starting_time,
        rate=rate,
        electrode=electrode or mock_IntracellularElectrode(),
        gain=gain,
        capacitance_slow=capacitance_slow,
        resistance_comp_correction=resistance_comp_correction,
    )


def mock_CurrentClampSeries(
    name=None,
    data=None,
    electrode=None,
    gain=0.02,
    stimulus_description="N/A",
    bias_current=None,
    bridge_balance=None,
    capacitance_compensation=None,
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
):
    return CurrentClampSeries(
        name=name if name is not None else name_generator("CurrentClampSeries"),
        data=data if data is not None else np.ones((30,)),
        electrode=electrode or mock_IntracellularElectrode(),
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


def mock_CurrentClampStimulusSeries(
    name=None,
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
):
    return CurrentClampStimulusSeries(
        name=name or name_generator("CurrentClampStimulusSeries"),
        data=data if data is not None else np.ones((30,)),
        electrode=electrode or mock_IntracellularElectrode(),
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


def mock_IZeroClampSeries(
    name=None,
    data=None,
    electrode=None,
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
):
    return IZeroClampSeries(
        name=name or name_generator("IZeroClampSeries"),
        data=data if data is not None else np.ones((30,)),
        electrode=electrode or mock_IntracellularElectrode(),
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


def mock_IntracellularRecordingsTable(n_rows=5):
    irt = IntracellularRecordingsTable()
    for _ in range(n_rows):
        electrode = mock_IntracellularElectrode()
        irt.add_recording(
            electrode=electrode,
            stimulus=mock_VoltageClampStimulusSeries(electrode=electrode),
            response=mock_VoltageClampSeries(electrode=electrode),
        )
