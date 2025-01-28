from pynwb import NWBHDF5IO

from pynwb.testing.mock.file import mock_Subject, mock_NWBFile

from pynwb.testing.mock.base import mock_TimeSeries

from pynwb.testing.mock.ophys import (
    mock_ImagingPlane,
    mock_OnePhotonSeries,
    mock_TwoPhotonSeries,
    mock_RoiResponseSeries,
    mock_PlaneSegmentation,
    mock_OpticalChannel,
    mock_Fluorescence,
    mock_DfOverF,
    mock_ImageSegmentation,
)

from pynwb.testing.mock.ogen import (
    mock_OptogeneticStimulusSite,
    mock_OptogeneticSeries
)

from pynwb.testing.mock.device import mock_Device

from pynwb.testing.mock.behavior import (
    mock_Position,
    mock_PupilTracking,
    mock_CompassDirection,
    mock_SpatialSeries,
)

from pynwb.testing.mock.ecephys import (
    mock_ElectrodeGroup,
    mock_ElectrodeTable,
    mock_ElectricalSeries,
    mock_SpikeEventSeries,
    mock_Units,
)

from pynwb.testing.mock.icephys import (
    mock_IntracellularElectrode,
    mock_CurrentClampSeries,
    mock_IZeroClampSeries,
    mock_VoltageClampSeries,
    mock_VoltageClampStimulusSeries,
    mock_CurrentClampStimulusSeries,
    mock_IntracellularRecordingsTable,
)

import pytest

from pynwb.testing.mock.utils import name_generator, name_generator_registry

mock_functions = [
    mock_ImagingPlane,
    mock_OnePhotonSeries,
    mock_TwoPhotonSeries,
    mock_RoiResponseSeries,
    mock_PlaneSegmentation,
    mock_OpticalChannel,
    mock_Fluorescence,
    mock_DfOverF,
    mock_ImageSegmentation,
    mock_OptogeneticStimulusSite,
    mock_OptogeneticSeries,
    mock_Device,
    mock_Position,
    mock_PupilTracking,
    mock_CompassDirection,
    mock_SpatialSeries,
    mock_ElectrodeGroup,
    mock_ElectrodeTable,
    mock_ElectricalSeries,
    mock_SpikeEventSeries,
    mock_Subject,
    mock_NWBFile,
    mock_TimeSeries,
    mock_CurrentClampSeries,
    mock_IZeroClampSeries,
    mock_VoltageClampSeries,
    mock_VoltageClampStimulusSeries,
    mock_IntracellularElectrode,
    mock_CurrentClampStimulusSeries,
    mock_IntracellularRecordingsTable,
    mock_Units,
]


@pytest.mark.parametrize("mock_function", mock_functions)
def test_mock(mock_function):
    mock_function()


def test_mock_TimeSeries_w_timestamps():
    ts = mock_TimeSeries(timestamps=[0, 1, 2, 3])
    assert ts.timestamps is not None
    assert len(ts.timestamps) == 4


def test_mock_TimeSeries_w_no_time():
    ts = mock_TimeSeries()
    assert ts.rate == 10.0


@pytest.mark.parametrize("mock_function", mock_functions)
def test_mock_write(mock_function, tmp_path):
    if mock_function is mock_NWBFile:
        return
    nwbfile = mock_NWBFile()
    assert mock_function(nwbfile=nwbfile) is not None

    test_file = tmp_path / (mock_function.__name__ + ".nwb")
    with NWBHDF5IO(test_file, "w") as io:
        io.write(nwbfile)


def test_name_generator():

    name_generator_registry.clear()  # reset registry

    assert name_generator("TimeSeries") == "TimeSeries"
    assert name_generator("TimeSeries") == "TimeSeries2"

